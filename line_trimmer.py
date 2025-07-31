# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGIS Line Trimmer
                                 A QGIS plugin
 Corta automaticamente linhas quando elas se cruzam e garante vértices compartilhados.
 ***************************************************************************/
"""

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QTimer
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsGeometry,
    QgsPointXY,
    QgsWkbTypes,
)

from functools import partial
import os.path
import resources_rc


class LineTrimmer:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n', f'LineTrimmer_{locale}.qm')

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&QGIS Line Trimmer')
        self.enabled = False
        self.action = None

    def tr(self, message):
        return QCoreApplication.translate('LineTrimmer', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True,
                   add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.setCheckable(True)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        if add_to_menu:
            self.iface.addPluginToVectorMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icons', 'icon.png')
        self.action = self.add_action(
            icon_path,
            text=self.tr(u'Ativar/Desativar Line Trimmer'),
            callback=self.toggle_plugin,
            parent=self.iface.mainWindow()
        )
        self.enabled = False

    def unload(self):
        for action in self.actions:
            self.iface.removePluginVectorMenu(self.tr(u'&QGIS Line Trimmer'), action)
            self.iface.removeToolBarIcon(action)
        self.actions = []
        self.action = None

    def toggle_plugin(self):
        if self.enabled:
            self.disable_plugin()
        else:
            self.enable_plugin()

    def enable_plugin(self):
        self.enabled = True
        self.action.setChecked(True)
        self.iface.messageBar().pushMessage(
            "Line Trimmer",
            "Plugin ativado - Linhas serão cortadas automaticamente ao cruzar com linhas existentes",
            level=0,
            duration=3
        )
        QgsProject.instance().layerWasAdded.connect(self.on_layer_added)
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer) and layer.geometryType() == QgsWkbTypes.LineGeometry:
                self.connect_layer_signals(layer)

    def disable_plugin(self):
        self.enabled = False
        self.action.setChecked(False)
        self.iface.messageBar().pushMessage("Line Trimmer", "Plugin desativado", level=0, duration=3)
        try:
            QgsProject.instance().layerWasAdded.disconnect(self.on_layer_added)
        except Exception:
            pass
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer) and layer.geometryType() == QgsWkbTypes.LineGeometry:
                self.disconnect_layer_signals(layer)

    def on_layer_added(self, layer):
        if isinstance(layer, QgsVectorLayer) and layer.geometryType() == QgsWkbTypes.LineGeometry:
            self.connect_layer_signals(layer)

    def connect_layer_signals(self, layer):
        if self.enabled:
            try:
                layer.featureAdded.disconnect()
            except Exception:
                pass
            layer.featureAdded.connect(partial(self.defer_feature_processing, layer))

    def disconnect_layer_signals(self, layer):
        try:
            layer.featureAdded.disconnect()
        except Exception:
            pass

    def defer_feature_processing(self, layer, feature_id):
        QTimer.singleShot(0, lambda: self.on_feature_added(layer, feature_id))

    def on_feature_added(self, layer, feature_id):
        if not isinstance(layer, QgsVectorLayer) or layer.geometryType() != QgsWkbTypes.LineGeometry:
            return

        feature = layer.getFeature(feature_id)
        if not feature.isValid():
            return

        # Verifica e corta linha se necessário
        self.check_and_trim_line(layer, feature)

        # SALVA a linha (modificada ou não) e reativa adicionar linha
        if layer.isEditable():
            layer.triggerRepaint()
            layer.commitChanges()
            layer.startEditing()
            self.iface.actionAddFeature().trigger()  # Reativa ferramenta adicionar linha

    def check_and_trim_line(self, layer, new_feature):
        new_geometry = new_feature.geometry()
        if not new_geometry or new_geometry.isEmpty():
            return

        if not layer.isEditable():
            self.iface.messageBar().pushMessage(
                "Line Trimmer",
                "Erro: camada não está em modo edição.",
                level=2,
                duration=5
            )
            return

        for existing_feature in layer.getFeatures():
            if existing_feature.id() == new_feature.id():
                continue

            existing_geometry = existing_feature.geometry()
            if not existing_geometry or existing_geometry.isEmpty():
                continue

            if new_geometry.intersects(existing_geometry):
                intersection = new_geometry.intersection(existing_geometry)
                if intersection and not intersection.isEmpty():
                    trimmed_geometry = self.trim_line_at_intersection(new_geometry, intersection)
                    if trimmed_geometry:
                        layer.changeGeometry(new_feature.id(), trimmed_geometry)

                        self.insert_shared_vertex(layer, existing_feature, intersection)

                        temp_feature = new_feature
                        temp_feature.setGeometry(trimmed_geometry)
                        self.insert_shared_vertex(layer, temp_feature, intersection)

                        self.iface.messageBar().pushMessage(
                            "Line Trimmer",
                            "Linha cortada e vértices compartilhados nas duas linhas",
                            level=0,
                            duration=2
                        )
                    break  # Processa apenas o primeiro corte encontrado

    def trim_line_at_intersection(self, line_geom, intersection_geom):
        if not line_geom or line_geom.isEmpty():
            return None

        if line_geom.isMultipart():
            lines = line_geom.asMultiPolyline()
            if not lines:
                return None
            points = lines[0]
        else:
            points = line_geom.asPolyline()

        if not points or len(points) < 2:
            return None

        if QgsWkbTypes.geometryType(intersection_geom.wkbType()) != QgsWkbTypes.PointGeometry:
            return None

        if intersection_geom.isMultipart():
            intersection_points = intersection_geom.asMultiPoint()
            if not intersection_points:
                return None
            intersect_point = intersection_points[0]
        else:
            intersect_point = intersection_geom.asPoint()

        insert_index = -1
        for i in range(len(points) - 1):
            seg_start = points[i]
            seg_end = points[i + 1]
            seg_geom = QgsGeometry.fromPolylineXY([seg_start, seg_end])
            dist = seg_geom.distance(QgsGeometry.fromPointXY(intersect_point))
            if dist < 1e-6:
                insert_index = i + 1
                break

        if insert_index == -1:
            return None

        new_points = points[:insert_index]
        last_point = new_points[-1]
        if last_point.distance(intersect_point) > 1e-9:
            new_points.append(intersect_point)

        if len(new_points) < 2:
            return None

        return QgsGeometry.fromPolylineXY(new_points)

    def insert_shared_vertex(self, layer, feature, intersection_geom):
        if not intersection_geom or not feature or not feature.isValid():
            return

        if QgsWkbTypes.geometryType(intersection_geom.wkbType()) != QgsWkbTypes.PointGeometry:
            return

        if intersection_geom.isMultipart():
            points = intersection_geom.asMultiPoint()
        else:
            points = [intersection_geom.asPoint()]

        if not points:
            return

        geom = feature.geometry()
        if geom.isMultipart():
            polylines = geom.asMultiPolyline()
            if not polylines:
                return
            polyline = polylines[0]
        else:
            polyline = geom.asPolyline()

        if not polyline:
            return

        tolerance = 1e-9
        modified = False

        for point in points:
            exists = any(point.distance(existing_point) < tolerance for existing_point in polyline)
            if exists:
                continue

            min_dist = float('inf')
            insert_index = -1
            for i in range(len(polyline) - 1):
                seg_geom = QgsGeometry.fromPolylineXY([polyline[i], polyline[i + 1]])
                dist = seg_geom.distance(QgsGeometry.fromPointXY(point))
                if dist < min_dist and dist < 1e-6:
                    insert_index = i + 1
                    min_dist = dist

            if insert_index != -1:
                polyline.insert(insert_index, point)
                modified = True

        if modified and len(polyline) >= 2:
            new_geom = QgsGeometry.fromPolylineXY(polyline)
            layer.changeGeometry(feature.id(), new_geom)
