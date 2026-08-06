# math585-qc-companion

Duke Math 585 (Algorithmic Trading) 教材的**配套代码仓库**。教授书稿里的例子
大多不是按 QuantConnect 写的,这个 repo 把它们迁移成能在 LEAN 里实际跑起来的
算法,一个例子一个文件夹。目的是验证书里的结论,并记录迁移过程中哪些地方
需要改、为什么。

这里放的是**教学演示代码**,不是生产策略。

## 命名规则

每个演示放在一个独立文件夹里,命名为:

```
ch{章}-{节}-{短名}
```

短名用小写英文加连字符,不带空格。例如:

```
ch03-2-mean-reversion/
ch07-1-vwap-execution/
ch11-4-kelly-sizing/
```

## 每个文件夹的内容

```
ch03-2-mean-reversion/
├── main.py        # LEAN 算法本体
├── config.json    # LEAN 项目配置(lean project-create 生成)
└── NOTES.md       # 从 ../NOTES_TEMPLATE.md 复制后填写
```

`NOTES.md` 是这个 repo 的重点 —— 代码跑通只是一半,另一半是写下书里
的写法和 QC API 的写法差在哪。

## 环境

```powershell
conda env create -f environment.yml   # 首次,或在另一台机器上复现
conda activate qc
lean --version
```

`environment.yml` 记录的是 Windows 上建出来的 `qc` 环境,pip 依赖
(`lean`、`quantconnect-stubs`)是跨平台的,在 Mac 上同样可用。

## 不进 git 的东西

`data/`(LEAN 市场数据)、`backtests/`(回测输出)、书稿 PDF。
PDF 统一放在 `../pdfs/`,那个目录不受任何 git 管理。
