# Project CBM Menu Repo Setup Notes

This ZIP is laid out so you can drop it into your private GitHub repository:

```text
https://github.com/cdaters/project-cbm-menu
```

## Recommended first commit

```bash
mkdir -p ~/dev/project-cbm-menu
cd ~/dev/project-cbm-menu
unzip ~/Downloads/Project-CBM-v6.5-Menu-Repo-Bundle.zip
# move contents out of the root folder if needed

git init
git add .
git commit -m "Initial Project CBM Menu v6.5 source bundle"
git branch -M main
git remote add origin git@github.com:cdaters/project-cbm-menu.git
git push -u origin main
```

## Build the redistributable menu bundle

```bash
make bundle
```

Output:

```text
dist/Project-CBM-v6.5-Bundle.zip
```

## Opinionated version guidance

Yes: keep the public Project CBM image version and the private menu-system version separate.

Use:

```text
Project CBM v1.0.0 image
Project CBM Menu v6.5
```

That gives you room to keep refining the private build diary and scripts without making every internal menu change look like a public image release.
