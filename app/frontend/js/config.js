const CONFIG = {
    appName: "Chronos",
    version: "1.0.0",
    apiBaseUrl: "http://localhost:8000/api/v1",
    
    // Thinking indicator messages
    thinkingStages: [
        { delay: 0, message: "Consulting archives..." },
        { delay: 1000, message: "Analyzing historical contexts..." },
        { delay: 2000, message: "Formatting response..." }
    ],
    
    // Default suggestions
    suggestions: [
        "Tell me about Ancient Egyptian pyramids",
        "How did the Nile shape Egyptian civilization?",
        "What was daily life like in Ancient Egypt?"
    ]
};