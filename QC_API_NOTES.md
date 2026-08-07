# QuantConnect API 速查

写算法时最常撞上的几个概念。每条只讲"是什么 / 什么时候用",配一个最小示例。

> ## 每条都标了来源,读的时候先看标签
>
> - **`[源码]`** —— 从本机已安装的 `quantconnect-stubs`、LEAN CLI 源码或实际运行
>   输出核对过。签名、类型、枚举值属于这类。
> - **`[判断]`** —— 经验性推断,**没有直接依据**。用法建议、性能说法、"通常怎么
>   怎么样"属于这类。**拿去讲课或写进书稿之前,自己先验一遍。**
>
> 不确定归哪类的,一律归 `[判断]`。
>
> 核对方法有个坑:在 `.pyi` 里全文搜 `def cash(` 会匹配到别的类的同名成员,得到
> 看起来权威、实际错位的答案。要**先定位类的行范围,再在范围内搜**。

> **命名规则** `[源码]` —— 现在的 Python API 是 snake_case。书稿里是旧版
> PascalCase,对应关系:方法名 `SetStartDate` → `set_start_date`,枚举成员
> `Resolution.Daily` → `Resolution.DAILY`,属性 `self.Portfolio` → `self.portfolio`。
> (依据:`lean project-create` 生成的模板 `main.py` 全部使用 snake_case。)

---

## `initialize` 和 `on_data` 什么时候被调用

`on_data` 在**每来一个新数据点时**被调用一次,是策略逻辑的入口。 `[源码]`
(依据:模板 `main.py` 的 docstring 原文 —— "on_data event is the primary entry
point for your algorithm. Each new data point will be pumped in here.")

`initialize` 在回测最开始**只跑一次**,用来做一次性设置:日期、资金、订阅哪些
标的、建哪些指标。这时候还没有任何行情数据。 `[判断]`
(合乎观察到的行为,但我没有从源码或官方文档核实"只调用一次"这个断言。)

调用频率由你订阅数据时选的 `Resolution` 决定。 `[判断]`

```python
def initialize(self):
    self.set_cash(100000)          # 只执行一次

def on_data(self, data: Slice):
    self.debug(self.time)          # 每个数据点执行一次
```

---

## 指标的 `is_ready` 是什么意思,不检查会怎样

指标有 `is_ready` 属性,返回布尔值。 `[源码]`
(依据:`QuantConnect/Indicators/__init__.pyi`,`def is_ready(self) -> bool`。)

含义是"我攒够数据了吗"—— 指标需要积累足够多的历史数据才能算出有意义的值,比如
100 日均线在第 100 根 K 线之前算不出来。 `[判断]`

**不检查的后果**:指标会返回 0 或者用不完整数据算出的值,你拿它去比大小会在回测
开头得到一串假信号。这类 bug 很隐蔽,统计结果看起来"能跑",只是错的。 `[判断]`

```python
def on_data(self, data: Slice):
    if not self.sma_long.is_ready:
        return                     # 卫语句:没就绪就别往下走
```

---

## `set_warm_up` 的作用

有四个重载,`bar_count: int` 和 `time_span: timedelta` 各两个(可选再带一个
`resolution` 参数)。所以传整数根数和传时间跨度都合法。 `[源码]`
(依据:`QuantConnect/Algorithm/__init__.pyi`,四条 `def set_warm_up` 签名。)

`is_warming_up` 属性存在,返回布尔值。 `[源码]`

作用是预热:让 LEAN 在正式回测开始前先喂一段历史数据给指标,这样回测第一天指标
就已经 ready。不预热的话,要么浪费掉回测开头一段,要么靠 `is_ready` 挡着空转。
预热期间 `on_data` 也会被调用,但 `is_warming_up` 为真。 `[判断]`

```python
def initialize(self):
    self.set_warm_up(100)          # 预热 100 根
```

---

## `set_holdings` 和 `market_order` 的区别

两个都是下单,区别在**用什么单位描述你要多少**。

| | 签名里的关键参数 | 来源 |
| --- | --- | --- |
| `set_holdings(symbol, percentage, ...)` | `percentage: float` | `[源码]` |
| `market_order(symbol, quantity, ...)` | `quantity: int` 或 `float` | `[源码]` |
| `liquidate(symbol=None, ...)` | symbol 可省略 | `[源码]` |

(依据:`QuantConnect/Algorithm/__init__.pyi` 的三组签名。)

- `set_holdings` 的 `percentage` 是**占组合的比例**,`0.5` = 总资产的 50%。 `[源码]`
  (参数名和类型直接来自签名。)
- `market_order` 的 `quantity` 是**具体股数**。正数买、**负数卖** —— 负数表示
  卖出这一点签名里看不出来,是我的推断。 `[判断]`
- 日常策略用 `set_holdings` 更多,因为通常想的是"仓位多重"而不是"买几股";需要
  精确控制股数(比如期权对冲)才用 `market_order`。 `[判断]`

```python
self.set_holdings("SPY", 0.5)      # 半仓
self.market_order("SPY", 100)      # 买 100 股
self.liquidate("SPY")              # 清掉这个标的的全部仓位
```

---

## `Resolution` 的取值和含义

五个取值,整数枚举: `[源码]`
(依据:`QuantConnect/__init__.pyi` 第 1439 行起,`class Resolution(IntEnum)`。)

| 取值 | 枚举值 | 含义 | 一天调用 `on_data` 大约几次 |
| --- | --- | --- | --- |
| `Resolution.TICK` | 0 | 逐笔 | 几万到几百万 `[判断]` |
| `Resolution.SECOND` | 1 | 每秒 | ~23,400 `[判断]` |
| `Resolution.MINUTE` | 2 | 每分钟 | ~390 `[判断]` |
| `Resolution.HOUR` | 3 | 每小时 | ~7 `[判断]` |
| `Resolution.DAILY` | 4 | 每天 | 1 `[判断]` |

**取值和枚举数字是 `[源码]`,右边那一列是 `[判断]`** —— 那是我按美股常规交易时段
6.5 小时算出来的(6.5×60=390 分钟,×60=23,400 秒),不是从任何文档读来的。实际
次数还受盘前盘后、半日市、数据缺失影响。

精度越细回测越慢、占的磁盘越大;做日线级别的策略用 `DAILY` 就够,用 `MINUTE`
只是白白慢几百倍。 `[判断]`

```python
self.add_equity("SPY", Resolution.DAILY)
```

---

## `self.portfolio` 和 `self.securities` 里有什么

`portfolio` 返回 `SecurityPortfolioManager`,`securities` 返回 `SecurityManager`。 `[源码]`
(依据:`QuantConnect/Algorithm/__init__.pyi`。)

`SecurityPortfolioManager` 上已核实的成员: `[源码]`

| 成员 | 类型 |
| --- | --- |
| `cash` | `float` |
| `invested` | `bool` |
| `total_portfolio_value` | `float` |
| `total_unrealized_profit` | `float` |

`SecurityHolding.quantity` → `float`,`Security.price` → `float`。 `[源码]`
(依据:`QuantConnect/Securities/__init__.pyi`,分别限定在
`SecurityPortfolioManager`、`SecurityHolding`、`Security` 三个类的行范围内搜到。)

一句话记:portfolio 回答"我怎么样",securities 回答"这个标的怎么样"。 `[判断]`

```python
self.portfolio.cash                    # 剩余现金
self.portfolio.total_portfolio_value   # 总资产
self.portfolio.invested                # 有没有持仓(布尔)
self.portfolio["SPY"].quantity         # SPY 持有股数
self.securities["SPY"].price           # SPY 最新价
```

---

## 名词表

这份笔记和这个仓库里会出现的软件工程术语,一句话解释。整节都是 `[判断]` ——
通用解释,不针对 QuantConnect,没有对应的源码依据。

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
| **stubs** | 只有类型签名、没有实现的 `.pyi` 文件。给编辑器做自动补全用,也是核对 API 签名最快的地方。 |
| **slug** | 用于命名的短标识,只用小写字母和连字符,不带空格。比如 `sma-crossover`。 |
