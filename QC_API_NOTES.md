# QuantConnect API 速查

写算法时最常撞上的几个概念。每条只讲"是什么 / 什么时候用",配一个最小示例。

> **命名规则**:现在的 Python API 是 snake_case。书稿里的旧写法是 PascalCase,
> 对应关系:方法名 `SetStartDate` → `set_start_date`,枚举成员
> `Resolution.Daily` → `Resolution.DAILY`,属性 `self.Portfolio` → `self.portfolio`。

---

## `initialize` 和 `on_data` 什么时候被调用

`initialize` 在回测最开始**只跑一次**,用来做一次性设置:日期、资金、订阅哪些
标的、建哪些指标。这时候还没有任何行情数据。

`on_data` 在**每来一个新数据点时**被调用一次,是策略逻辑的入口。调用频率由你
订阅数据时选的 `Resolution` 决定。

```python
def initialize(self):
    self.set_cash(100000)          # 只执行一次

def on_data(self, data: Slice):
    self.debug(self.time)          # 每个数据点执行一次
```

---

## 指标的 `is_ready` 是什么意思,不检查会怎样

指标需要积累够足够多的历史数据才能算出有意义的值。比如 100 日均线,在第 100 根
K 线之前它算不出来。`is_ready` 就是"我攒够数据了吗"这个开关。

**不检查的后果**:指标会返回 0 或者用不完整数据算出的值。你拿它去比大小,会在
回测开头得到一串假信号 —— 而且这类 bug 很隐蔽,统计结果看起来"能跑",只是错的。

```python
def on_data(self, data: Slice):
    if not self.sma_long.is_ready:
        return                     # 卫语句:没就绪就别往下走
```

---

## `set_warm_up` 的作用

预热。它让 LEAN 在**正式回测开始之前**先喂一段历史数据给你的指标,这样回测第一天
指标就已经是 ready 的了。

不预热的话,你要么浪费掉回测区间开头的一大段(等指标 ready),要么就得靠上面那个
`is_ready` 挡着空转。预热期间 `on_data` 也会被调用,但 `self.is_warming_up` 为真。

```python
def initialize(self):
    self.set_warm_up(100)          # 预热 100 根,够 100 日均线用
```

---

## `set_holdings` 和 `market_order` 的区别

两个都是下单,区别在**用什么单位描述你要多少**。

- `set_holdings(symbol, 比例)` —— **按占组合的比例**。`0.5` = 把总资产的 50% 放在
  这个标的上。LEAN 自己算该买卖多少股。想清仓就传 `0`。
- `market_order(symbol, 股数)` —— **按具体股数**。正数买,负数卖。

日常策略用 `set_holdings` 更多,因为你通常想的是"仓位多重",不是"买几股"。
需要精确控制股数(比如期权对冲)才用 `market_order`。

```python
self.set_holdings("SPY", 0.5)      # 半仓
self.market_order("SPY", 100)      # 买 100 股
self.liquidate("SPY")              # 清掉这个标的的全部仓位
```

---

## `Resolution` 的取值和含义

订阅数据时选的**时间精度**,直接决定 `on_data` 被调用的频率。

| 取值 | 含义 | 一天调用 `on_data` 大约几次 |
| --- | --- | --- |
| `Resolution.TICK` | 逐笔 | 几万到几百万 |
| `Resolution.SECOND` | 每秒 | ~23,400 |
| `Resolution.MINUTE` | 每分钟 | ~390 |
| `Resolution.HOUR` | 每小时 | ~7 |
| `Resolution.DAILY` | 每天 | 1 |

精度越细,回测越慢、占的磁盘越大。做日线级别的策略(比如双均线)就该用 `DAILY`,
用 `MINUTE` 只是白白慢几百倍。

```python
self.add_equity("SPY", Resolution.DAILY)
```

---

## `self.portfolio` 和 `self.securities` 里有什么

- **`self.portfolio`** —— 你的**账户状态**:现在有多少钱、持仓值多少、赚了多少。
  `self.portfolio.invested` 是最常用的:有任何持仓就为真。
- **`self.securities`** —— 你**订阅的每个标的**的信息:最新价、是否可交易、
  手续费模型等。按代码索引。

一句话记:portfolio 回答"我怎么样",securities 回答"这个标的怎么样"。

```python
self.portfolio.cash                    # 剩余现金
self.portfolio.total_portfolio_value   # 总资产
self.portfolio.invested                # 有没有持仓(布尔)
self.portfolio["SPY"].quantity         # SPY 持有股数
self.securities["SPY"].price           # SPY 最新价
```

---

## 名词表

这份笔记和这个仓库里会出现的软件工程术语,一句话解释:

| 词 | 是什么 |
| --- | --- |
| **repo**(仓库) | 一个被 git 管理的文件夹。git 记录每次改动,可以随时回退到任意历史版本。 |
| **commit** | 一次存档。把当前改动打包记进 git 历史,附一句说明。 |
| **Docker** | 一种"把整套运行环境打包成一个盒子"的技术。LEAN 引擎跑在这个盒子里,所以你不用自己装 .NET 和一堆依赖。 |
| **镜像**(image) | 那个盒子的模板文件。`quantconnect/lean:latest` 就是一个镜像,占 42.5 GB。 |
| **容器**(container) | 由镜像启动起来的、正在运行的实例。每次 `lean backtest` 就起一个。 |
| **JSON** | 一种纯文本的数据格式,用 `{}` 和 `:` 表示键值对。`config.json`、`lean.json` 都是这种格式,可以直接用记事本改。 |
| **CLI** | 命令行工具。`lean` 就是一个 CLI,在终端里敲命令用,没有图形界面。 |
| **卫语句**(guard clause) | 一种写法:函数开头先检查前提条件,不满足就立刻 `return`,避免整段逻辑再套一层缩进。 |
| **slug** | 用于命名的短标识,只用小写字母和连字符,不带空格。比如 `sma-crossover`。 |
