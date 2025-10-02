# FoundationAgents/OpenManus

[FoundationAgents]() / **[OpenManus]()** Public

 

 main

Code

May 20, 2025

 |
 

Mar 15, 2025

 |
 

Sep 14, 2025

 |
 

Aug 13, 2025

 |
 

Jul 27, 2025

 |
 

Mar 29, 2025

 |
 

Jul 27, 2025

 |
 

Mar 18, 2025

 |
 

Mar 18, 2025

 |
 

Mar 6, 2025

 |
 

Apr 22, 2025

 |
 

Jul 23, 2025

 |
 

May 20, 2025

 |
 

Mar 16, 2025

 |
 

Mar 6, 2025

 |
 

Sep 4, 2025

 |
 

May 27, 2025

 |
 

May 27, 2025

 |
 

May 27, 2025

 |
 

Jun 5, 2025

 |
 

Jul 22, 2025

 |
 

May 22, 2025

 |
 

Mar 28, 2025

 |
 

Mar 21, 2025

 |
 

Jul 19, 2025

 |
 

May 20, 2025

 |

English | [中文]() | [한국어]() | [日本語]()

# 👋 OpenManus

Manus is incredible, but OpenManus can achieve any idea without an _Invite Code_ 🛫!

Our team members [@Xinbin Liang]() and [@Jinyu Xiang]() (core authors), along with [@Zhaoyang Yu](), [@Jiayi Zhang](), and [@Sirui Hong](), we are from [@MetaGPT](). The prototype is launched within 3 hours and we are keeping building!

It's a simple implementation, so we welcome any suggestions, contributions, and feedback!

Enjoy your own agent with OpenManus!

We're also excited to introduce [OpenManus-RL](), an open-source project dedicated to reinforcement learning (RL)- based (such as GRPO) tuning methods for LLM agents, developed collaboratively by researchers from UIUC and OpenManus.

## Project Demo

seo\_website.mp4

## Installation

We provide two installation methods. Method 2 (using uv) is recommended for faster installation and better dependency management.

### Method 1: Using conda

1.  Create a new conda environment:

```shell
conda create -n open_manus python=3.12
conda activate open_manus
```

2.  Clone the repository:

```shell
git clone https://github.com/FoundationAgents/OpenManus.git
cd OpenManus
```

3.  Install dependencies:

```shell
pip install -r requirements.txt
```

### Method 2: Using uv (Recommended)

1.  Install uv (A fast Python package installer and resolver):

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2.  Clone the repository:

```shell
git clone https://github.com/FoundationAgents/OpenManus.git
cd OpenManus
```

3.  Create a new virtual environment and activate it:

```shell
uv venv --python 3.12
source .venv/bin/activate  # On Unix/macOS
# Or on Windows:
# .venv\Scripts\activate
```

4.  Install dependencies:

```shell
uv pip install -r requirements.txt
```

### Browser Automation Tool (Optional)

```shell
playwright install
```

## Configuration

OpenManus requires configuration for the LLM APIs it uses. Follow these steps to set up your configuration:

1.  Create a `config.toml` file in the `config` directory (you can copy from the example):

```shell
cp config/config.example.toml config/config.toml
```

2.  Edit `config/config.toml` to add your API keys and customize settings:

```toml
# Global LLM configuration
[llm]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."  # Replace with your actual API key
max_tokens = 4096
temperature = 0.0

# Optional configuration for specific LLM models
[llm.vision]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."  # Replace with your actual API key
```

## Quick Start

One line for run OpenManus:

```shell
python main.py
```

Then input your idea via terminal!

For MCP tool version, you can run:

```shell
python run_mcp.py
```

For unstable multi-agent version, you also can run:

```shell
python run_flow.py
```

### Custom Adding Multiple Agents

Currently, besides the general OpenManus Agent, we have also integrated the DataAnalysis Agent, which is suitable for data analysis and data visualization tasks. You can add this agent to `run_flow` in `config.toml`.

```toml
# Optional configuration for run-flow
[runflow]
use_data_analysis_agent = true     # Disabled by default, change to true to activate
```

In addition, you need to install the relevant dependencies to ensure the agent runs properly: [Detailed Installation Guide]()

## How to contribute

We welcome any friendly suggestions and helpful contributions! Just create issues or submit pull requests.

Or contact @mannaandpoem via 📧email: [mannaandpoem@gmail.com]()

**Note**: Before submitting a pull request, please use the pre-commit tool to check your changes. Run `pre-commit run --all-files` to execute the checks.

## Community Group

Join our networking group on Feishu and share your experience with other developers!

## Star History

## Sponsors

Thanks to [PPIO]() for computing source support.

> PPIO: The most affordable and easily-integrated MaaS and GPU cloud solution.

## Acknowledgement

Thanks to [anthropic-computer-use](), [browser-use]() and [crawl4ai]() for providing basic support for this project!

Additionally, we are grateful to [AAAJ](), [MetaGPT](), [OpenHands]() and [SWE-agent]().

We also thank stepfun(阶跃星辰) for supporting our Hugging Face demo space.

OpenManus is built by contributors from MetaGPT. Huge thanks to this agent community!

## Cite

```bibtex
@misc{openmanus2025,
  author = {Xinbin Liang and Jinyu Xiang and Zhaoyang Yu and Jiayi Zhang and Sirui Hong and Sheng Fan and Xiao Tang},
  title = {OpenManus: An open-source framework for building general AI agents},
  year = {2025},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.15186407},
  url = {https://doi.org/10.5281/zenodo.15186407},
}
```

## About

No fortress, purely open ground. OpenManus is Coming.

## [Packages ]()

No packages published

