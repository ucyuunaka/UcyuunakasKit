根据我的需求和提示词的撰写改写规范 撰写我需要的提示词：

当前需求：

待修改提示词：

提示词撰写规范【重要】：


**Prompt design** (提示词设计) is the process of creating prompts, or natural language requests, that elicit accurate, high quality responses from a language model.

This page introduces basic concepts, strategies, and best practices to get you started designing prompts to get the most out of AI models.

> **Note:** Prompt engineering is iterative. These guidelines and templates are starting points. Experiment and refine based on your specific use cases and observed model responses.

---

## Clear and specific instructions

An effective and efficient way to customize model behavior is to provide it with clear and specific instructions. Instructions can be in the form of a question, step-by-step tasks, or as complex as mapping out a user's experience and mindset.

### Input

Input is the required text in the prompt that you want the model to provide a response to. Inputs can be a:
*   **Question input:** A question that the model answers.
*   **Task input:** A task the model performs.
*   **Entity input:** An entity the model operates on.
*   **Completion input:** Partial input that the model completes or continues.

| Input type | Prompt | Generated output |
| :--- | :--- | :--- |
| **Question** | What's a good name for a flower shop that specializes in selling bouquets of dried flowers? Create a list of 5 options with just the names. | Here are 10 names for a flower shop specializing in dried flowers:<br>1. Everlasting Blooms<br>2. Dried & Delightful<br>3. The Petal Preserve<br>4. Whispers of Wildflowers<br>5. Forever Blooms |
| **Task** | Give me a simple list of just the things that I must bring on a camping trip. The list should have 5 items. | 1. **Tent:** Your shelter from the elements.<br>2. **Sleeping Bag:** Stay warm and comfortable.<br>3. **Sleeping Pad:** Insulation and cushioning for a good night's sleep.<br>4. **Headlamp or Flashlight:** Light for nighttime activities.<br>5. **First Aid Kit:** Be prepared for minor injuries. |
| **Entity** | Classify the following items as [large, small]:<br>Elephant<br>Mouse<br>Snail | Here's the classification:<br>* **Elephant:** Large<br>* **Mouse:** Small<br>* **Snail:** Small |

#### Partial input completion

Generative language models work like an advanced auto completion tool. When you provide partial content, the model can provide the rest of the content or what it thinks is a continuation of that content as a response. When doing so, if you include any examples or context, the model can take those examples or context into account.

The following example provides a prompt with an instruction and an entity input:

**Prompt:**
```json
For the given order, return a JSON object that has the fields cheeseburger, hamburger, fries, or drink, with the value being the quantity.
Order: A burger and a drink.
```

**Response:**
```json
{ "cheeseburger": 0, "hamburger": 1, "fries": 0, "drink": 1 }
```

While the model did as prompted, writing out the instructions in natural language can sometimes be challenging and it leaves a lot to the model's interpretation. To reduce the size of the JSON response (omitting items not ordered), you can give an example and a [response prefix](https://ai.google.dev/gemini-api/docs/prompting-strategies#prefixes) and let the model complete it:

**Prompt:**
```text
Valid fields are cheeseburger, hamburger, fries, and drink.
Order: Give me a cheeseburger and fries
Output: ``` { "cheeseburger": 1, "fries": 1 } ```
Order: I want two burgers, a drink, and fries.
Output:
```

**Response:**
```json
{ "hamburger": 2, "drink": 1, "fries": 1 }
```

### Constraints

Specify any constraints on reading the prompt or generating a response. You can tell the model what to do and not to do.

**Prompt:**
```text
Summarize this text in one sentence:
Text: A quantum computer exploits quantum mechanical phenomena to perform calculations exponentially faster than any modern traditional computer. At very tiny scales, physical matter acts as both particles and as waves, and quantum computing uses specialized hardware to leverage this behavior. The operating principles of quantum devices is beyond the scope of classical physics. When deployed at scale, quantum computers could be used in a wide variety of applications such as: in cybersecurity to break existing encryption methods while helping researchers create new ones, in meteorology to develop better weather forecasting etc. However, the current state of the art quantum computers are still largely experimental and impractical.
```

**Response:**
```text
Exploiting quantum mechanical phenomena, quantum computers can perform calculations exponentially faster than traditional computers for potential applications like cybersecurity and meteorology, although they are currently largely experimental and impractical.
```

### Response format

You can give instructions that specify the format of the response (table, bulleted list, elevator pitch, keywords, JSON, etc.).

**System instruction:**
```text
All questions should be answered comprehensively with details, unless the user requests a concise response specifically.
```

**Prompt:**
```text
What is a smart way to make a business that sells DVD's in 2025?
```

**Response:**
```text
Starting a business selling DVDs in 2025 presents significant challenges due to the overwhelming dominance of digital streaming...
1. Extreme Niche Specialization: You cannot compete with streaming libraries. Your business must focus on what digital doesn't offer easily or at all. This could include:
* Out-of-Print & Rare Titles...
```

#### Format responses with the completion strategy

The [completion strategy](https://ai.google.dev/gemini-api/docs/prompting-strategies#completion) can also help format the response.

**Prompt:**
```text
Create an outline for an essay about hummingbirds.
I. Introduction
*
```

**Response:**
```text
Okay, here is an outline for an essay about hummingbirds, starting from the introduction you provided:
I. Introduction
* Hook: Start with a captivating fact or description about hummingbirds...
* Background: Briefly introduce hummingbirds...
* Thesis Statement: State the main point of the essay...
```

---

## Zero-shot vs few-shot prompts

*   **Zero-shot prompts:** Prompts that provide no examples.
*   **Few-shot prompts:** Prompts that contain a few examples to show the model what "getting it right" looks like.

We recommend **always including few-shot examples** in your prompts. Prompts without few-shot examples are likely to be less effective.

**Zero-shot Example:**

**Prompt:**
```text
Please choose the best explanation to the question:
Question: How is snow formed?
Explanation1: Snow is formed when water vapor in the air freezes into ice crystals in the atmosphere...
Explanation2: Water vapor freezes into ice crystals forming snow.
Answer:
```

**Response:**
```text
Explanation1 is the better explanation because it provides more detail...
```

**Few-shot Example (Preference for conciseness):**

**Prompt:**
```text
Below are some examples showing a question, explanation, and answer format:

Question: Why is the sky blue?
Explanation1: The sky appears blue because of Rayleigh scattering, which causes shorter blue wavelengths...
Explanation2: Due to Rayleigh scattering effect.
Answer: Explanation2

Question: What is the cause of earthquakes?
Explanation1: Sudden release of energy in the Earth's crust.
Explanation2: Earthquakes happen when tectonic plates suddenly slip or break apart...
Answer: Explanation1

Now, Answer the following question given the example formats above:
Question: How is snow formed?
Explanation1: Snow is formed when water vapor in the air freezes into ice crystals in the atmosphere...
Explanation2: Water vapor freezes into ice crystals forming snow.
Answer:
```

**Response:**
```text
Answer: Explanation2
```

### Optimal number of examples
Models like Gemini can often pick up on patterns using a few examples. Experiment with the number. Too many examples may cause the model to [overfit](https://developers.google.com/machine-learning/glossary#overfitting).

### Patterns vs anti patterns
Using examples to show the model a **pattern to follow** is more effective than using examples to show an anti-pattern to avoid.

⛔ **Negative pattern:**
```text
Don't end haikus with a question:
Haiku are fun
A short and simple poem
Don't you enjoy them?
```

✅ **Positive pattern:**
```text
Always end haikus with an assertion:
Haiku are fun
A short and simple poem
A joy to write
```

### Consistent formatting
Make sure that the structure and formatting of few-shot examples are the same (XML tags, white spaces, newlines, example splitters).

---

## Add context

Include instructions and information (context) the model needs to solve a problem, rather than assuming it knows everything.

**Poor Prompt:**
```text
What should I do to fix my disconnected wifi? The light on my Google Wifi router is yellow and blinking slowly.
```
*(Response is usually generic troubleshooting)*

**Better Prompt (with Context):**
```text
Answer the question using the text below. Respond with only the text provided.

Question: What should I do to fix my disconnected wifi? The light on my Google Wifi router is yellow and blinking slowly.

Text:
Color: Slowly pulsing yellow
What it means: There is a network error.
What to do: Check that the Ethernet cable is connected to both your router and your modem and both devices are turned on. You might need to unplug and plug in each device again.
... (other router status codes) ...
```

**Response:**
```text
Check that the Ethernet cable is connected to both your router and your modem and both devices are turned on. You might need to unplug and plug in each device again.
```

---

## Add prefixes

A prefix is a word or phrase added to the prompt content.

*   **Input prefix:** Signals semantically meaningful parts of the input (e.g., "English:", "French:").
*   **Output prefix:** Gives the model information about expected response format (e.g., "JSON:").
*   **Example prefix:** Labels in few-shot prompts.

**Example:**
**Prompt:**
```text
Classify the text as one of the following categories.
- large
- small

Text: Rhino
The answer is: large

Text: Mouse
The answer is: small

Text: Elephant
The answer is:
```

**Response:**
```text
The answer is: large
```

---

## Break down prompts into components

For complex use cases:

1.  **Break down instructions:** Create one prompt per instruction and choose based on user input.
2.  **Chain prompts:** For sequential steps, the output of one prompt becomes the input of the next.
3.  **Aggregate responses:** Perform parallel tasks on different data portions and aggregate results.

---

## Prompt iteration strategies

1.  **Use different phrasing:**
    *   *v1:* How do I bake a pie?
    *   *v2:* Suggest a recipe for a pie.
    *   *v3:* What's a good pie recipe?

2.  **Switch to an analogous task:** If direct instructions fail, frame it differently.
    *   *Instead of:* "Which category does The Odyssey belong to: thriller, sci-fi, mythology, biography" (might yield a sentence).
    *   *Try:* "Multiple choice problem: Which of the following options describes the book The Odyssey? Options: ..."

3.  **Change the order of prompt content:**
    *   Try permutations of `[examples]`, `[context]`, and `[input]`.

---

## Fallback responses

If the model returns a fallback response (e.g., "I'm not able to help with that..."), usually due to safety filters, try **increasing the temperature**.

---

## Things to avoid

*   Avoid relying on models to generate factual information (hallucinations).
*   Use with care on math and logic problems.

---

## Gemini 3 Best Practices

The following practices are recommended for optimal results with Gemini 3:

### Core prompting principles
*   **Be precise and direct:** State goals clearly. Avoid fluff.
*   **Use consistent structure:** Use XML-style tags (`<context>`, `<task>`) or Markdown headings consistently.
*   **Define parameters:** Explain ambiguous terms.
*   **Control output verbosity:** Explicitly request detailed or concise responses.
*   **Handle multimodal inputs coherently:** Treat text, images, and audio as equal inputs.
*   **Prioritize critical instructions:** Put constraints and persona in System Instructions.
*   **Structure for long contexts:** Context first -> Specific instructions/questions at the very **end**.
*   **Anchor context:** Use transition phrases like "Based on the information above...".

### Enhancing reasoning and planning
Prompt the model to plan or self-critique.

**Example - Explicit planning:**
```text
Before providing the final answer, please:
1. Parse the stated goal into distinct sub-tasks.
2. Check if the input information is complete.
3. Create a structured outline to achieve the goal.
```

**Example - Self-critique:**
```text
Before returning your final response, review your generated output against the user's original constraints.
1. Did I answer the user's *intent*, not just their literal words?
2. Is the tone authentic to the requested persona?
```

### Structured prompting examples

**XML example:**
```xml
<role>
You are a helpful assistant.
</role>

<constraints>
1. Be objective.
2. Cite sources.
</constraints>

<context>
[Insert User Input Here]
</context>

<task>
[Insert the specific user request here]
</task>
```

**Markdown example:**
```markdown
# Identity
You are a senior solution architect.

# Constraints
- No external libraries allowed.
- Python 3.11+ syntax only.

# Output format
Return a single code block.
```

### Example template combining best practices

**System Instruction:**
```xml
<role>
You are a specialized assistant for [Insert Domain, e.g., Data Science].
You are precise, analytical, and persistent.
</role>

<instructions>
1. **Plan**: Analyze the task and create a step-by-step plan.
2. **Execute**: Carry out the plan.
3. **Validate**: Review your output against the user's task.
4. **Format**: Present the final answer in the requested structure.
</instructions>

<constraints>
- Verbosity: [Specify Low/Medium/High]
- Tone: [Specify Formal/Casual/Technical]
</constraints>

<output_format>
Structure your response as follows:
1. **Executive Summary**: [Short overview]
2. **Detailed Response**: [The main content]
</output_format>
```

**User Prompt:**
```xml
<context>
[Insert relevant documents, code snippets, or background info here]
</context>

<task>
[Insert specific user request here]
</task>

<final_instruction>
Remember to think step-by-step before answering.
</final_instruction>
```

---

## Agentic workflows

For deep agentic workflows, control how the model reasons, plans, and executes.

### Dimensions of behavior

1.  **Reasoning and strategy:**
    *   **Logical decomposition:** Analyzing constraints/prerequisites.
    *   **Problem diagnosis:** Depth of analysis (abductive reasoning).
    *   **Information exhaustiveness:** Speed vs. thoroughness trade-off.

2.  **Execution and reliability:**
    *   **Adaptability:** Pivoting when data contradicts assumptions.
    *   **Persistence and Recovery:** Self-correcting errors.
    *   **Risk Assessment:** Distinguishing between read (low risk) and write (high risk) actions.

3.  **Interaction and output:**
    *   **Ambiguity and permission handling:** When to ask for clarification.
    *   **Verbosity:** Explaining actions vs. silent execution.
    *   **Precision and completeness:** Exact figures vs. estimates.

### System instruction template (Agentic)

The following system instruction improves performance on complex agentic benchmarks.

```text
You are a very strong reasoner and planner. Use these critical instructions to structure your plans, thoughts, and responses.

Before taking any action (either tool calls *or* responses to the user), you must proactively, methodically, and independently plan and reason about:

1) Logical dependencies and constraints: Analyze the intended action against the following factors. Resolve conflicts in order of importance:
    1.1) Policy-based rules, mandatory prerequisites, and constraints.
    1.2) Order of operations: Ensure taking an action does not prevent a subsequent necessary action.
        1.2.1) The user may request actions in a random order, but you may need to reorder operations to maximize successful completion of the task.
    1.3) Other prerequisites (information and/or actions needed).
    1.4) Explicit user constraints or preferences.

2) Risk assessment: What are the consequences of taking the action? Will the new state cause any future issues?
    2.1) For exploratory tasks (like searches), missing *optional* parameters is a LOW risk. **Prefer calling the tool with the available information over asking the user, unless** your `Rule 1` (Logical Dependencies) reasoning determines that optional information is required for a later step in your plan.

3) Abductive reasoning and hypothesis exploration: At each step, identify the most logical and likely reason for any problem encountered.
    3.1) Look beyond immediate or obvious causes. The most likely reason may not be the simplest and may require deeper inference.
    3.2) Hypotheses may require additional research. Each hypothesis may take multiple steps to test.
    3.3) Prioritize hypotheses based on likelihood, but do not discard less likely ones prematurely. A low-probability event may still be the root cause.

4) Outcome evaluation and adaptability: Does the previous observation require any changes to your plan?
    4.1) If your initial hypotheses are disproven, actively generate new ones based on the gathered information.

5) Information availability: Incorporate all applicable and alternative sources of information, including:
    5.1) Using available tools and their capabilities
    5.2) All policies, rules, checklists, and constraints
    5.3) Previous observations and conversation history
    5.4) Information only available by asking the user

6) Precision and Grounding: Ensure your reasoning is extremely precise and relevant to each exact ongoing situation.
    6.1) Verify your claims by quoting the exact applicable information (including policies) when referring to them. 

7) Completeness: Ensure that all requirements, constraints, options, and preferences are exhaustively incorporated into your plan.
    7.1) Resolve conflicts using the order of importance in #1.
    7.2) Avoid premature conclusions: There may be multiple relevant options for a given situation.
        7.2.1) To check for whether an option is relevant, reason about all information sources from #5.
        7.2.2) You may need to consult the user to even know whether something is applicable. Do not assume it is not applicable without checking.
    7.3) Review applicable sources of information from #5 to confirm which are relevant to the current state.

8) Persistence and patience: Do not give up unless all the reasoning above is exhausted.
    8.1) Don't be dissuaded by time taken or user frustration.
    8.2) This persistence must be intelligent: On *transient* errors (e.g. please try again), you *must* retry **unless an explicit retry limit (e.g., max x tries) has been reached**. If such a limit is hit, you *must* stop. On *other* errors, you must change your strategy or arguments, not repeat the same failed call.

9) Inhibit your response: only take an action after all the above reasoning is completed. Once you've taken an action, you cannot take it back.
```