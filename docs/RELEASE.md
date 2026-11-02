# Checklist de release — v2.0.0

## Antes do merge

- [ ] `develop` com CI verde.
- [ ] Todos os testes passando localmente.
- [ ] `python -m compileall -q src tests` sem erros.
- [ ] README, docs e CHANGELOG atualizados.
- [ ] Wiki publicada.
- [ ] Página web publicada no GitHub Pages.
- [ ] Nenhum segredo ou arquivo local rastreado.
- [ ] Issues 1 a 13 fechadas ou com pendências documentadas.

## Release

```bash
git checkout develop
git pull origin develop
git checkout -b release/v2.0.0
# ajustes finais de versão e documentação
git commit -m "chore(release): prepara versão 2.0.0"
git push origin release/v2.0.0
```

Abrir pull request de `release/v2.0.0` para `main`, revisar e fazer merge.

## Tag e release no GitHub

```bash
git checkout main
git pull origin main
git tag -a v2.0.0 -m "CaosZero 2.0.0"
git push origin v2.0.0
```

Criar a release no GitHub com:

- título `CaosZero 2.0.0`;
- descrição baseada no `CHANGELOG.md`;
- tag `v2.0.0`;
- artefatos: código-fonte e, opcionalmente, pacote wheel.

## Depois do merge

- [ ] Sincronizar `main` de volta em `develop`.
- [ ] Confirmar workflow de release.
- [ ] Confirmar GitHub Pages.
- [ ] Confirmar links da wiki.
- [ ] Conferir branch protection em `main`.
- [ ] Ensaiar a apresentação com a versão tagueada.

## Sincronização

```bash
git checkout develop
git pull origin develop
git merge origin/main --no-edit
git push origin develop
```

## Critérios de aceite

- Tag `v2.0.0` publicada.
- Release notes com mudanças e instruções de uso.
- `main` e `develop` sincronizadas.
- Demonstração reproduzível em menos de 12 minutos.
- CI verde em `main`.
