# QGIS Line Trimmer Plugin

## Visão Geral

O plugin **QGIS Line Trimmer** é uma ferramenta desenvolvida para otimizar o processo de digitalização de linhas no QGIS. Ele detecta automaticamente interseções entre a linha que está sendo digitalizada e as linhas existentes na camada ativa, cortando a nova linha no ponto de interseção e mantendo apenas a parte inicial da linha.

## Funcionalidades

- **Corte Automático de Linhas**: Ao digitalizar uma nova linha, se ela cruzar uma linha existente na mesma camada, a nova linha será automaticamente truncada no ponto de interseção.
- **Preservação da Parte Inicial**: Apenas a porção da nova linha que precede o ponto de interseção é mantida, facilitando a criação de geometrias limpas e conectadas.
- **Integração com Ferramentas de Digitalização**: O plugin se integra perfeitamente com as ferramentas de digitalização padrão do QGIS.

## Instalação

Para instalar o plugin QGIS Line Trimmer, siga os passos abaixo:

1.  **Baixe o plugin**: Faça o download do arquivo ZIP do plugin (disponível em breve no repositório oficial do QGIS ou no GitHub).
2.  **Localize o diretório de plugins do QGIS**: No QGIS, vá em `Configurações > Opções > Sistema` e procure por 'Caminhos de plugins Python'. O caminho padrão geralmente é `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins` no Linux, ou similar em outros sistemas operacionais.
3.  **Extraia o plugin**: Descompacte o conteúdo do arquivo ZIP baixado (a pasta `qgis_line_trimmer`) para o diretório de plugins do QGIS.
4.  **Ative o plugin**: Reinicie o QGIS. Em seguida, vá em `Plugins > Gerenciar e Instalar Plugins...`, procure por "QGIS Line Trimmer" e marque a caixa para ativá-lo.

## Como Usar

1.  **Ativar o Plugin**: Após a instalação, o plugin estará disponível na barra de ferramentas do QGIS. Clique no ícone do plugin (um ícone de linha com uma tesoura, por exemplo) para ativá-lo ou desativá-lo. Uma mensagem na barra de status do QGIS indicará se o plugin está ativo.
2.  **Iniciar Digitalização**: Selecione uma camada de linha no painel 'Camadas' e coloque-a em modo de edição (clique no ícone de lápis).
3.  **Adicionar Linha**: Selecione a ferramenta 'Adicionar Feição de Linha' (ou similar) e comece a digitalizar sua nova linha.
4.  **Corte Automático**: Se a linha que você está digitalizando cruzar uma linha existente na mesma camada, o plugin detectará a interseção e cortará automaticamente a nova linha no ponto de cruzamento. A parte da linha após a interseção será descartada.
5.  **Salvar Edições**: Após digitalizar suas linhas, salve as edições da camada para persistir as alterações.

## Desenvolvimento

Este plugin foi desenvolvido usando PyQGIS. O código-fonte está disponível no GitHub. Contribuições são bem-vindas!

## Licença

Este plugin é licenciado sob a GNU General Public License v2.0.

## Contato

Para dúvidas ou sugestões, entre em contato com god.rafa365@gmail.com.

