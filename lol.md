Crie uma aplicação web completa em Django chamada "SomTeca", uma biblioteca de músicas e playlists. É um projeto acadêmico do IFRS, então o código deve ser limpo, organizado, comentado em português e fácil de explicar.

## Tecnologias
- Python 3 + Django (versão estável mais recente)
- SQLite como banco de dados
- Bootstrap 5 (via CDN) para o visual, com tema escuro inspirado no Spotify
- Chart.js (via CDN) para os gráficos
- Pillow para upload de imagens
- Templates Django (sem React, sem API)

## Models (com relacionamentos)
1. **Artista**: nome, biografia, foto (ImageField), país de origem, data de criação
2. **Album**: título, artista (ForeignKey para Artista), ano de lançamento, capa (ImageField), gênero
3. **Musica**: título, álbum (ForeignKey para Album), artistas (ManyToMany para Artista, para permitir participações), arquivo de áudio (FileField, aceitando só .mp3), duração, número da faixa, contador de reproduções
4. **Playlist**: nome, descrição, capa (opcional), usuário dono (ForeignKey para User), músicas (ManyToMany para Musica usando uma tabela intermediária "ItemPlaylist" com ordem e data em que foi adicionada), pública ou privada
5. **Reproducao**: usuário, música e data/hora. Registra cada vez que uma música é tocada, para o ranking e o resumo do ano

## CRUD completo para Artistas, Álbuns, Músicas e Playlists
Para cada um:
- Cadastrar (formulário com validação)
- Listar (com paginação, de 12 em 12 itens, em cards)
- Visualizar detalhes
- Editar
- Excluir (com página de confirmação antes)
Use Class-Based Views (ListView, DetailView, CreateView, UpdateView, DeleteView) e ModelForms.

## Funcionalidades extras
1. **Player de MP3**: um player fixo no rodapé da página (como no Spotify), com play/pause, próxima, anterior, barra de progresso e volume, usando a tag <audio> do HTML5 e JavaScript puro. Ao clicar numa música ou playlist, ela começa a tocar. Cada reprodução deve ser registrada no banco com uma requisição fetch (POST com CSRF token) para uma view que cria um registro em Reproducao.

2. **Ranking de mais ouvidas**: página com o top 10 de músicas, artistas e álbuns mais tocados, com filtro por período (última semana, último mês, sempre) e gráfico de barras com Chart.js.

3. **Resumo do ano ("Retrospectiva")**: página personalizada do usuário logado, mostrando:
   - total de minutos ouvidos no ano
   - top 5 músicas e top 5 artistas
   - gênero favorito
   - mês em que mais ouviu música (gráfico de linha)
   - visual em estilo de "cards" coloridos, inspirado no Spotify Wrapped

4. **Autenticação**: cadastro, login e logout com django.contrib.auth. Só usuários logados podem criar playlists e ver a retrospectiva. Cada usuário só pode editar ou excluir as próprias playlists.

5. **Busca**: barra de busca no topo que procura em músicas, artistas e álbuns ao mesmo tempo (usando Q objects).

6. **Filtros**: filtrar músicas por gênero e álbuns por ano.

7. **Página inicial (dashboard)**: contadores (total de músicas, artistas, álbuns e playlists), músicas adicionadas recentemente e as mais tocadas da semana.

8. **Mensagens de feedback**: usar django.contrib.messages para mostrar "Música cadastrada com sucesso!" etc.

9. **Django Admin personalizado**: com list_display, search_fields e list_filter em todos os models.

## Estrutura
- Projeto: `somteca`
- Apps: `musica` (artistas, álbuns, músicas), `playlists` e `usuarios`
- Templates com herança (base.html com navbar, player e rodapé)
- Arquivos estáticos organizados em static/css e static/js
- Configurar MEDIA_URL e MEDIA_ROOT para os uploads

## Entregáveis
1. Todo o código, arquivo por arquivo, com o caminho de cada um
2. requirements.txt
3. Passo a passo para rodar: criar o ambiente virtual, instalar, rodar as migrations, criar o superusuário e iniciar o servidor
4. Um comando de gerenciamento (management command) `popular_banco` que cria dados de exemplo (artistas, álbuns, músicas e reproduções falsas) para testar o ranking e a retrospectiva
5. Um README.md explicando o projeto e as funcionalidades

Coloque models e views e templates em pastas.