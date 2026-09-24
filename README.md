# Dashboard de links

Uma homepage estática gerada por `builder.py`. Os links e seus grupos são configurados em `links.toml`.

## Publicar no GitHub Pages

1. Rode `python3 builder.py` para gerar o `index.html`.
2. Envie os arquivos do projeto para a branch `main`, incluindo o `index.html` gerado.
3. No repositório, abra **Settings → Pages**.
4. Em **Build and deployment**, escolha **Deploy from a branch**, selecione `main` e a pasta `/(root)`.

O Pages publica a raiz do repositório diretamente. Não é necessário instalar dependências nem configurar Actions. Depois de mudar `links.toml` ou os ícones, rode o builder de novo e envie a página gerada.

## Editar os links

Edite `links.toml`. Cada link usa uma seção `[[links]]`:

```toml
[[links]]
name = "Exemplo"
url = "https://example.com"
description = "Uma descrição curta"
group = "Favoritos"
icon = "mdi:star"
```

`name` e `url` são obrigatórios. `description`, `group` e `icon` são opcionais. O campo `icon` aceita nomes públicos do Iconify no formato `coleção:nome`, como `mdi:star` ou `simple-icons:github`. Esses ícones são carregados pelo componente oficial do Iconify a partir da API pública, então precisam de internet no navegador. Sem `icon`, o builder procura um PNG ou ICO local em `media/icons/`, usando o nome do link em minúsculas e com palavras separadas por hífen: por exemplo, `Google Drive` procura `media/icons/google-drive.png` e depois `media/icons/google-drive.ico`. PNG tem preferência se ambos existirem. Se nenhum arquivo for encontrado, a página mostra a inicial do nome.

O builder usa `tomllib`, incluído no Python 3.11 ou mais recente, e gera HTML estático. Mantenha `index.html`, `style.css`, `links.toml` e a pasta `media/icons/` na raiz para servir pelo Pages.
# dashy
