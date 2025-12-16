# Llama Guard: AI Safety through Content Moderation
Developed by Meta, Llama Guard models are fine-tuned from the main Llama Generative models (such as Llama 3.1/3.2)
to classify content as safe or unsafe based on the MLCommons standardized Hazard Taxonomy.
- Llama Guard 3-8B: Built on Llama-3.1-8B, specifically fine-tuned for content safety classification tasks
  with optimized inference patterns.
- Generates structured text responses indicating safety status and violated content categories,
  enabling programmatic integration with existing safety pipelines.
- Provides content moderation in 8 languages with specialized optimization for search queries and code interpreter tool calls.
- Supports 14 hazard categories including Hate Speech, Misinformation, Violence, Self-Harm, and more.
