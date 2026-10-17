# Gitee 镜像下载

GitHub 在校园网偶尔不稳定，可用 Gitee 镜像。

## 在线浏览（不用注册）

镜像地址发布后在此填写：

```
https://gitee.com/<账号>/medstats-pharm-skills
```

## 打包下载

仓库页面点「克隆/下载 → 下载 ZIP」，解压后按 [README.md](README.md) 方式 A 使用。

## git 克隆

```bash
git clone https://gitee.com/<账号>/medstats-pharm-skills.git
```

## 同步策略（给维护者）

一个仓库两个远端，推送时两边都推：

```bash
git remote add origin https://github.com/<账号>/medstats-pharm-skills.git
git remote add gitee https://gitee.com/<账号>/medstats-pharm-skills.git
git push origin main
git push gitee main
```

或在 Gitee 仓库设置中开启「自动同步 GitHub」。

> 注：镜像地址在阿索建好 GitHub/Gitee 仓库后补全。
