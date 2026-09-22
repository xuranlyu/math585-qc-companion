# math585-qc-companion

Duke Math 585 (Algorithmic Trading) 教材的**配套代码仓库**。教授书稿里的例子
大多不是按 QuantConnect 写的,这个 repo 把它们迁移成能在 LEAN 里实际跑起来的
算法,一个例子一个文件夹。目的是验证书里的结论,并记录迁移过程中哪些地方
需要改、为什么。

这里放的是**教学演示代码**,不是生产策略。

## 先试一个读者实验

[Alpha 与条件期望](conditional-alpha/)（v5.7 Ch5）：15 分钟的交互 notebook。
在实验页面点击 **Run in QuantConnect**，复制到自己的账户后打开 `research.ipynb`、Run All。
可以修改 benchmark、概率和信息分组，观察 alpha、残差和预测误差。

## 命名规则

每个演示放在一个独立文件夹里,**只用主题 slug,不带章号**:

```
sma-crossover/
mean-reversion/
vwap-execution/
```

小写英文加连字符,不带空格。

**为什么不带章号**:书稿还在改 —— 教授删过整章,章号全部前移过一次,以后还会
变。目录名一旦带章号,每次改版都要重命名一堆文件夹,git 历史也跟着乱。章节对应
关系统一记在 [INDEX.md](INDEX.md) 的"书里位置"一列,改版时只改那一张表。

## 每个文件夹的内容

```
sma-crossover/
├── main.py         # LEAN 算法本体
├── config.json     # LEAN 项目配置(lean project-create 生成)
├── research.ipynb  # 配套的研究用 notebook
└── NOTES.md        # 从 ../NOTES_TEMPLATE.md 复制后填写
```

## 仓库根目录的几份文档

- [INDEX.md](INDEX.md) —— 所有演示的总表,章节对应关系以此为准。
- [QC_API_NOTES.md](QC_API_NOTES.md) —— 常用 API 速查,含新旧写法对应和名词表。
- [NOTES_TEMPLATE.md](NOTES_TEMPLATE.md) —— 每个演示的笔记模板。

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

