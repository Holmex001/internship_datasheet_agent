# 任务指导书：基于 LangChain 的 LM377 数据手册智能体

## 目标

基于LangChain框架，制作一个，能够回答用户对某一型号芯片（如：LM337）的性能、应用等方面的问题的Agent。
交互方式：CLI

---

## 分工
- 爬虫 （黄钰惠） —— 已完成，代码在 C:\Users\ThinkBook\PycharmProjects\internship_pro_03\elecfans
- 封装tool + PPT模板
- agent框架
- 向量数据库
- CLI交互

---

## 爬虫
internship_pro_03\elecfans

### 结构
internship_pro_03\elecfans\main.py   主要函数
internship_pro_03\elecfans\downloads 已经下载好的数据手册，建数据库的同学先用这个目录下的PDF文件，后续可以用爬虫下载新的数据手册
internship_pro_03\elecfans\results.json  
spider.fetch_and_filter_results("LM337") 搜索到的结果，主要是厂商和型号的对应关系，后续可以用这个结果去下载数据手册
internship_pro_03\elecfans\top_companies.json    同一个芯片有不同厂家的数据手册，这个是大厂的名单，以它们的数据手册优先

### Cookie
一定时间后会失效，需要重新登录获取新的Cookie
位置在 .env 中的 ELECFANS_COOKIE
获取方式我会发一个视频在微信群中

---

## 封装tool + PPT模板
把爬虫获取pdf文件的功能封装成一个tool，供agent调用

相对简单，所以还要负责 PPT模板的制作

## agent框架
LangChain_learn/langChain_try.py 里面有我调用LLM的函数，可以参考

和课件中流程差不多
看后面详细的指导

## 向量数据库
最难的一部分

一定要确保效果，照着课件中方法抄，基本上效果都不行，不过我做出来效果还不错，那就能做出来

## CLI交互

可以不用CLI，CLI是最简单的交互方式
如果会一点前端，可以写一个网页，框架可以用 Vue、React、Streamlit 等等

难点就在要等其他人做好才能做，所以就不叫你做PPT模板了，要和做Agent好好了解清楚接口什么的。

---

## 配置
### env
将.env.example 复制为 .env

你们要商量好名字和EMBEDDING_BASE_URL（所有人都要一样，我用的硅基流动的）
如果有人需要加，也要说好

并配置好 ：

**agent的LLM：**
BASE_URL    agent的LLM的URL，比如https://api.deepseek.com
API_KEY     对应API_key
MODEL       模型名字

**文档向量化模型：（数据库）**
EMBEDDING_BASE_URL
EMBEDDING_API_KEY、
EMBEDDING_MODEL、

**爬虫网站cookie：获取方式微信看，每隔一段时间要更新，拿不到pdf先换cookie**
ELECFANS_COOKIE

**数据手册存放目录：**
DATASHEET_DIR

### python env
conda虚拟环境，名字随便起，里面安装好 requirements.txt 中的包

如果有需要其他包，记得在后面加

注意安装时，一定要在虚拟环境下(别在base里面使劲下东西)，python解释器也要调成你用的虚拟环境
比如：我的虚拟环境名字为 langchain，python解释器就要调成 langchain 这个虚拟环境的解释器，安装环境的时候也要在langchain下

```cmd
(base) PS C:\Users\ThinkBook\PycharmProjects\internship_pro_03> conda activate langchain
(langchain) PS C:\Users\ThinkBook\PycharmProjects\internship_pro_03> pip install -r .\requirements.txt

```

---

# AI给的指导书
满足约束，格式，但是可以在技术方法上改进
（）里面是我加的

## 🛠️ 第一阶段：核心技术选型与环境配置

在 AI 智能体工业化开发时代，LangChain 是打通大模型与外部资源的核心中间层框架。本项目的基础设施选型如下：

| 核心组件 | 技术选型 | 配置说明 |
| --- |------| --- |
| **大语言模型 (LLM)** | 随便   | 通过平台调用，API等信息存在.env中，统一使用 `init_chat_model` 接口初始化。

 |
| **嵌入模型 (Embedding)** | BAAI/bge-m3 | 使用 `SiliconFlowEmbeddings`，多语言支持极佳，向量维度 1024。（我用的硅基流动的API，模型就是这个，效果不差）

 |
| **文档加载 (Loader)** | `PyPDFLoader` | 支持布局模式 (`layout`) 提取 PDF 文本。

 |
| **向量数据库 (Vector DB)** | `Chroma` | 轻量级，开源免费，极适合开发测试与本地化检索。

 |
| **短期记忆 (Memory)** | `InMemorySaver` | 负责存储当前会话所有消息。

 |

---

## 🗄️ 第二阶段：知识入库流水线（RAG 核心构建）

RAG 流程中最关键的步骤是将非结构化的 PDF 数据手册转化为大模型可高效检索的向量数据，流程为：**检索 → 增强 → 生成**。

* **文档加载 (Load)：** 使用 `PyPDFLoader` 读取本地的数据手册pdf文件。该加载器会将异构数据源统一加载为内存中的标准化 `Document` 对象。


* **文档切分 (Transform)：** 文档拆分/分块是 RAG 流程中最具挑战性、最影响检索效果的核心环节。必须使用 `RecursiveCharacterTextSplitter`（递归字符切分器）。它能够优先在段落、句子等自然语言边界处进行拆分，从而最大程度保持手册参数的语义完整性。


* **向量化 (Embed)：** 依托文本嵌入模型，将自然语言文本转换为计算机可识别的高维稠密向量。语义相近的文本，在向量空间中的距离越近。


* **向量存储 (Store)：** 将生成的向量与原始文档块持久化保存至 `Chroma` 数据库的本地目录（如 `./chroma_vsdb`），避免重复计算向量成本。


---

## 🤖 第三阶段：工具定义与智能体大脑组装

智能体（Agent）是整个任务的调度中心，它能以大模型为推理核心，动态决策并自主调用工具完成复杂任务。

* **定义爬虫与检索工具 (Tools)：** 工具是赋予大语言模型与外部世界交互能力的关键组件。使用 `@tool` 装饰器将已有的 Python 爬虫脚本封装为工具。有效的工具必须具备原子性（单一明确功能）、描述清晰（包含输入格式与使用场景），并内置异常捕获。


* **构建 ReAct 引擎 (Agent)：** 使用 `create_agent()` 函数统一入口构建智能体。该智能体将按照 **Thought（推理） -> Action（行动） -> Observation（观察）** 的 ReAct 模式循环运行。当用户询问 LM377 参数时，Agent 会自主决定是否调用搜索下载工具，或直接查询 Chroma 数据库。


* **注入系统消息 (SystemMessage)：** 全局定义模型角色与业务规则。设定系统提示词（如：“你是专业的硬件工程师，必须基于工具检索到的 Datasheet 原文回答，严禁编造参数”）。此消息优先级最高，在多轮对话中固定保留。



---

## 🧠 第四阶段：上下文工程与 CLI 交互

原生大模型是无状态服务，不存储任何对话上下文。为了在 CLI 终端中实现多轮追问，必须引入上下文工程。

* **接入短期记忆：** 使用 `InMemorySaver` 创建内存级持久化器，并在 `create_agent` 时将其绑定给 Agent。


* **会话状态隔离：** 在 CLI 主循环中，定义包含 `thread_id` 的 `config` 字典。只要每次 `invoke` 传入相同的 `thread_id`，Agent 就能自动追加历史消息，实现记忆复用与连贯的对话交互。


* **流式输出 (Stream)：** 为了缓解用户等待的焦虑感，在 CLI 交互中推荐使用 `stream()` 方法。该方法不等待模型推理完成，而是实时返回每一个 Token 字符，模拟出极客风格的打字机效果。


（交互也可以使用前端界面，Vue、React、Streamlit 等框架均可实现。CLI 只是最简化的交互方式，看你擅长哪个）

---

## 最终效果

```
(langchain) PS C:\Users\ThinkBook\PycharmProjects\internship_pro_02> python -m datasheet_agent
输入器件型号开始，或输入 /help 查看命令。
>: LM337
1. FAIRCHILD - LM337
2. LINER - LM337
3. ONSEMI - LM337
4. STMICROELECTRONICS - LM337
请选择资料表 [1/2/3/4]: 4
资料表回答：
The active datasheet is for the STMICROELECTRONICS LM137/LM237/LM337 family. The   
LM337 is a three-terminal adjustable negative voltage regulator. It is described as
capable of supplying in excess of 1.5 A over a -1.2 V to -37 V output voltage      
range, with output voltage adjustable down to Vref, 0.01%/V typical line
regulation, 0.3% typical load regulation, ripple rejection of 77 dB, and standard  
3-lead transistor packages. The device includes current limit, thermal overload    
protection, and safe area protection, which remain functional even if the
adjustment terminal is disconnected.

For the LM337, the operating temperature range listed in the absolute maximum      
ratings/order codes is 0 to 125 °C. The input-output voltage differential absolute 
maximum is 40 V. Output current is listed as 1.5 A for TO-220/TO-3 and 0.5 A for   
TO-39. Total power dissipation is internally limited.

Electrical characteristics for LM337 are specified at 0 °C < Tj < 150 °C, VI - VO =
5 V, IO = 0.5 A unless otherwise specified. The LM337 reference voltage is -1.213 V
min, -1.25 V typ, -1.287 V max at Tamb = 25 °C; over Tmin ≤ Tj ≤ Tmax with 3 V ≤   
|VI - VO| ≤ 40 V, 10 mA ≤ |IO| ≤ |IO(max)|, P ≤ Pmax, it is -1.2 V min, -1.25 V    
typ, -1.3 V max. Adjustment pin current is 65 µA typ and 100 µA max. Minimum load  
current is 2.5 mA typ / 10 mA max for |VI - VO| ≤ 40 V and 1.5 mA typ / 6 mA max   
for |VI - VO| ≤ 10 V.

The datasheet shows typical applications including an adjustable negative voltage  
regulator, adjustable lab voltage regulator, -5.2 V regulator with electronic      
shutdown, and adjustable current regulator. For stability in the typical
application, C1 = 1 µF solid tantalum or 10 µF aluminium electrolytic is required; 
C2 = 1 µF solid tantalum is required only if the regulator is more than 10 cm from 
the power supply filter capacitor.
STMICROELECTRONICS / LM337 / 第 1 页
STMICROELECTRONICS / LM337 / 第 2 页
STMICROELECTRONICS / LM337 / 第 4 页
STMICROELECTRONICS / LM337 / 第 8 页
>: 讲解功能
资料表回答：
LM337 是三端可调负电压稳压器，属于 LM137/LM237/LM337
系列。它的核心功能是把负输入电压调节成稳定的负输出电压，输出电压范围为 -1.2 V 到   
-37 V，并且输出电压可调到
Vref。数据手册说明该系列器件只需要两个外部电阻即可设定输出电压。

从功能上看，LM337 主要用于负电源稳压。例如电路需要 -5 V、-12 V
或其他可调负电压轨时，可以用 LM337
产生稳定负电压。手册列出的典型应用包括“ADJUSTABLE NEGATIVE VOLTAGE
REGULATOR”（可调负电压稳压器）、“ADJUSTABLE LAB VOLTAGE
REGULATOR”（可调实验室电压稳压器）、“CURRENT
REGULATOR”（电流调节器）以及带保护二极管的负稳压器。

它的调节性能优于普通固定稳压器：典型线性调整率为 0.01%/V，典型负载调整率为
0.3%/V，纹波抑制为 77 dB。LM337 的参考电压 Vref 在 Tamb = 25 °C 时为 -1.213 V      
最小、-1.25 V 典型、-1.287 V 最大；在 Tmin ≤ Tj ≤ Tmax、3 V ≤ |VI - VO| ≤ 40 V、10 
mA ≤ |IO| ≤ |IO(max)|、P ≤ Pmax 条件下为 -1.2 V 最小、-1.25 V 典型、-1.3 V 最大。  

LM337
还集成了保护功能，包括限流、热过载保护和安全工作区保护。手册明确说明，即使调整端断 
开，所有过载保护电路仍保持完全有效。因此它不仅用于稳压，也适合需要一定容错和保护能 
力的负电源设计。

使用时需要注意稳定性外接电容：典型应用说明 C1 = 1 µF 固体钽电容或 10 µF
铝电解电容用于稳定；如果稳压器距离电源滤波电容超过 10 cm，则需要 C2 = 1 µF
固体钽电容；10 µF 电容可用于改善纹波抑制。
STMICROELECTRONICS / LM337 / 第 1 页
STMICROELECTRONICS / LM337 / 第 4 页
STMICROELECTRONICS / LM337 / 第 8 页
STMICROELECTRONICS / LM337 / 第 9 页
>: 输入电压范围
资料表回答：
LM337
数据手册没有给出一个独立的“输入电压范围”数值，而是用输入-输出电压差来限定：绝对最大
额定值中，VI - VO 输入输出电压差为 40 V。电气特性测试/保证条件中，多项参数是在 3 V 
≤ |VI - VO| ≤ 40 V
条件下给出的。因此设计时应把输入端与输出端之间的电压差控制在不超过 40
V；若希望满足数据手册电气特性条件，通常按 |VI - VO| 在 3 V 到 40 V
范围内理解。作为负压可调稳压器，它的输出电压范围为 -1.2 V 到 -37 V。
STMICROELECTRONICS / LM337 / 第 2 页
STMICROELECTRONICS / LM337 / 第 4 页
STMICROELECTRONICS / LM337 / 第 1 页
数据手册证据只明确给出了输入-输出电压差限制和输出电压范围，没有直接列出相对于地的固
定输入电压范围。
>: 讲解P5中的图片LOAD REGULATION
资料表回答：
P5 的 “LOAD REGULATION” 图是在说明 LM337 的负载调整率随温度变化的典型趋势。        

图中纵轴是 “OUTPUT VOLTAGE CHANGE (%)”，即输出电压变化百分比，范围大约从 +0.2% 到  
-1.4%。横轴是 “TEMPERATURE (°C)”，温度范围从 -75°C 到 +150°C。图内标出的测试条件是 
VI = -15 V、VO = -10 V。

图里有两条曲线：上方曲线标注为 IL = 0.5 A，下方曲线标注为 IL = 1.5
A。它们表示在相同输入/输出电压条件下，不同负载电流时，输出电压随温度变化产生的百分 
比偏移。

读图时可以这样理解：曲线越接近
0%，说明负载变化引起的输出电压变化越小，负载调整越好；曲线越往负方向偏，表示输出电 
压相对标称值下降得更多。图中 IL = 1.5 A 的曲线比 IL = 0.5 A
更低，说明重载时负载调整误差更大；温度升高后，尤其是 1.5 A
曲线，输出电压变化会进一步向负方向增加。按图形近似读数，IL = 0.5 A 在 25°C 附近约为
-0.1%，到 150°C 附近约为 -0.2%；IL = 1.5 A 在 25°C 附近约为 -0.25%，到 150°C       
附近约为 -0.8%。

结合电气特性表，LM337 的 KVO Load Regulation 在 Tamb = 25°C、10 mA ≤ |IO| ≤        
|IO(max)| 条件下，|VO| ≤ 5 V 时典型值 15 mV、最大值 50 mV；|VO| ≥ 5 V 时典型值     
0.3%、最大值 1%。因此 P5
图可以看作典型特性曲线，用来直观看温度和负载电流对输出电压变化的影响，而表格参数才 
是规定条件下的规格限值。
STMICROELECTRONICS / LM337 / 第 5 页 / LOAD REGULATION
STMICROELECTRONICS / LM337 / 第 5 页 / LOAD REGULATION
STMICROELECTRONICS / LM337 / 第 5 页 / LOAD REGULATION
STMICROELECTRONICS / LM337 / 第 4 页
>:

```

我在pdf读取的时候，除了文本还有图片，如果用户问到图片相关的地方，我会用OCR识别对应的图片内容，如果没时间或者你的模型不支持，那就算了。
语言上，我写的Agent和用户提问语言同步。
我写的，给了数据手册页码定位，有的话更好，但是数据库那边有点难，没时间也算了。
记忆上，默认以最近用户提到的型号为准