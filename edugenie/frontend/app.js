// =====================================================
// EduGenie Frontend
// =====================================================


// -----------------------------------------------------
// Helper
// -----------------------------------------------------

function $(id) {

    return document.getElementById(id);

}


// -----------------------------------------------------
// Tab navigation
// -----------------------------------------------------

document
    .querySelectorAll(".tab")
    .forEach((button) => {

        button.addEventListener(
            "click",
            () => {

                document
                    .querySelectorAll(".tab")
                    .forEach((tab) => {

                        tab.classList.remove(
                            "active"
                        );

                    });


                document
                    .querySelectorAll(".panel")
                    .forEach((panel) => {

                        panel.classList.remove(
                            "active"
                        );

                    });


                button.classList.add(
                    "active"
                );


                const panel =
                    $(button.dataset.tab);


                panel.classList.add(
                    "active"
                );

            }
        );

    });


// -----------------------------------------------------
// Example button
// -----------------------------------------------------

document
    .querySelectorAll(".example-button")
    .forEach((button) => {

        button.addEventListener(
            "click",
            () => {

                document
                    .querySelector(
                        '[data-tab="ask"]'
                    )
                    .click();


                $("askQuestion").value =
                    button.dataset.example;

            }
        );

    });


// -----------------------------------------------------
// Escape HTML
// -----------------------------------------------------

function escapeHtml(value) {

    return String(value)
        .replace(
            /[&<>"']/g,
            function (character) {

                const entities = {

                    "&": "&amp;",

                    "<": "&lt;",

                    ">": "&gt;",

                    '"': "&quot;",

                    "'": "&#039;"

                };

                return entities[
                    character
                ];

            }
        );

}


// -----------------------------------------------------
// Show result
// -----------------------------------------------------

function showResult(
    elementId,
    html
) {

    const element = $(elementId);

    element.innerHTML = html;

    element.classList.remove(
        "hidden"
    );

}


// -----------------------------------------------------
// Loading
// -----------------------------------------------------

function showLoading(
    elementId
) {

    showResult(
        elementId,
        `
        <p>
            EduGenie is thinking...
        </p>
        `
    );

}


// -----------------------------------------------------
// API helper
// -----------------------------------------------------

async function apiRequest(
    endpoint,
    data
) {

    const response =
        await fetch(
            endpoint,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(data)
            }
        );


    const result =
        await response.json();


    if (!response.ok) {

        throw new Error(
            result.detail ||
            "Request failed."
        );

    }


    return result;

}


// =====================================================
// ASK
// =====================================================

async function askQuestion() {

    showLoading(
        "askResult"
    );


    try {

        const question =
            $("askQuestion")
                .value
                .trim();


        if (!question) {

            throw new Error(
                "Please enter a question."
            );

        }


        const result =
            await apiRequest(
                "/api/ask",
                {
                    question:
                        question,

                    level:
                        $("askLevel")
                            .value
                }
            );


        showResult(
            "askResult",
            `
            <h4>Answer</h4>

            <p>
                ${escapeHtml(
                    result.answer
                ).replace(
                    /\n/g,
                    "<br>"
                )}
            </p>
            `
        );

    }

    catch (error) {

        showResult(
            "askResult",
            `
            <strong>
                Error
            </strong>

            <p>
                ${escapeHtml(
                    error.message
                )}
            </p>
            `
        );

    }

}


// =====================================================
// EXPLAIN
// =====================================================

async function explainTopic() {

    showLoading(
        "explainResult"
    );


    try {

        const topic =
            $("explainTopic")
                .value
                .trim();


        if (!topic) {

            throw new Error(
                "Please enter a topic."
            );

        }


        const result =
            await apiRequest(
                "/api/explain",
                {
                    topic:
                        topic,

                    level:
                        $("explainLevel")
                            .value
                }
            );


        showResult(
            "explainResult",
            `
            <h4>
                Explanation
            </h4>

            <p>
                ${escapeHtml(
                    result.answer
                ).replace(
                    /\n/g,
                    "<br>"
                )}
            </p>
            `
        );

    }

    catch (error) {

        showResult(
            "explainResult",
            `
            <strong>
                Error
            </strong>

            <p>
                ${escapeHtml(
                    error.message
                )}
            </p>
            `
        );

    }

}


// =====================================================
// QUIZ
// =====================================================

let currentQuiz = [];


async function generateQuiz() {

    showLoading(
        "quizResult"
    );


    try {

        const topic =
            $("quizTopic")
                .value
                .trim();


        const count =
            Number(
                $("quizCount").value
            );


        if (!topic) {

            throw new Error(
                "Please enter a quiz topic."
            );

        }


        const result =
            await apiRequest(
                "/api/quiz",
                {
                    topic:
                        topic,

                    num_questions:
                        count,

                    level:
                        $("quizLevel")
                            .value
                }
            );


        currentQuiz =
            result.questions;


        let html = `

            <h4>
                ${escapeHtml(
                    result.title
                )}
            </h4>

        `;


        result.questions
            .forEach(
                (question, index) => {

                    html += `

                    <div
                        class="quiz-question"
                    >

                        <h4>

                            ${index + 1}.
                            ${escapeHtml(
                                question.question
                            )}

                        </h4>

                    `;


                    question.options
                        .forEach(
                            (option, optionIndex) => {

                                html += `

                                <label
                                    class="option"
                                >

                                    <input
                                        type="radio"
                                        name="question-${index}"
                                        value="${optionIndex}"
                                    >

                                    ${escapeHtml(
                                        option
                                    )}

                                </label>

                                `;

                            }
                        );


                    html += `

                    </div>

                    `;

                }
            );


        html += `

            <button
                class="primary"
                onclick="gradeQuiz()"
            >
                Check Score
            </button>

            <div
                id="scoreArea"
            ></div>

        `;


        showResult(
            "quizResult",
            html
        );

    }

    catch (error) {

        showResult(
            "quizResult",
            `
            <strong>
                Error
            </strong>

            <p>
                ${escapeHtml(
                    error.message
                )}
            </p>
            `
        );

    }

}


// -----------------------------------------------------
// Grade quiz
// -----------------------------------------------------

function gradeQuiz() {

    let score = 0;


    currentQuiz.forEach(
        (question, index) => {

            const selected =
                document.querySelector(
                    `input[name="question-${index}"]:checked`
                );


            if (!selected) {

                return;

            }


            const selectedIndex =
                Number(
                    selected.value
                );


            const selectedAnswer =
                question.options[
                    selectedIndex
                ];


            if (
                selectedAnswer ===
                question.correct_answer
            ) {

                score++;

            }

        }
    );


    const percentage =
        Math.round(
            (score /
                currentQuiz.length) *
            100
        );


    $("scoreArea").innerHTML = `

        <p class="score">

            Score:
            ${score}/${currentQuiz.length}

            (${percentage}%)

        </p>

    `;

}


// =====================================================
// LEARNING PATH
// =====================================================

async function generatePath() {

    showLoading(
        "pathResult"
    );


    try {

        const goal =
            $("pathGoal")
                .value
                .trim();


        const weeks =
            Number(
                $("pathWeeks").value
            );


        if (!goal) {

            throw new Error(
                "Please enter your learning goal."
            );

        }


        const result =
            await apiRequest(
                "/api/learning-path",
                {
                    goal:
                        goal,

                    current_level:
                        $("pathLevel")
                            .value,

                    weeks:
                        weeks
                }
            );


        let html = `

            <h4>
                ${escapeHtml(
                    result.title
                )}
            </h4>

            <p>
                ${escapeHtml(
                    result.overview
                )}
            </p>

            <p>

                <strong>
                    Study time:
                </strong>

                ${result.estimated_hours_per_week}
                hours per week

            </p>

        `;


        result.steps.forEach(
            (step) => {

                html += `

                    <div
                        class="path-step"
                    >

                        <h4>

                            Week ${step.week}:
                            ${escapeHtml(
                                step.topic
                            )}

                        </h4>

                        <p>

                            <strong>
                                Objective:
                            </strong>

                            ${escapeHtml(
                                step.objective
                            )}

                        </p>

                        <p>
                            <strong>
                                Activities:
                            </strong>
                        </p>

                        <ul>

                            ${step.activities
                                .map(
                                    activity =>
                                        `<li>
                                            ${escapeHtml(
                                                activity
                                            )}
                                        </li>`
                                )
                                .join("")}

                        </ul>

                        <p>

                            <strong>
                                Milestone:
                            </strong>

                            ${escapeHtml(
                                step.milestone
                            )}

                        </p>

                    </div>

                `;

            }
        );


        html += `

            <h4>
                Study Tips
            </h4>

            <ul>

                ${result.tips
                    .map(
                        tip =>
                            `<li>
                                ${escapeHtml(
                                    tip
                                )}
                            </li>`
                    )
                    .join("")}

            </ul>

        `;


        showResult(
            "pathResult",
            html
        );

    }

    catch (error) {

        showResult(
            "pathResult",
            `
            <strong>
                Error
            </strong>

            <p>
                ${escapeHtml(
                    error.message
                )}
            </p>
            `
        );

    }

}


// =====================================================
// SUMMARY
// =====================================================

async function summarizeText() {

    showLoading(
        "summaryResult"
    );


    try {

        const text =
            $("summaryText")
                .value
                .trim();


        if (!text) {

            throw new Error(
                "Please paste some educational text."
            );

        }


        if (text.length < 20) {

            throw new Error(
                "Please enter at least 20 characters."
            );

        }


        const result =
            await apiRequest(
                "/api/summarize",
                {
                    text:
                        text,

                    level:
                        $("summaryLevel")
                            .value
                }
            );


        showResult(
            "summaryResult",
            `

            <h4>
                Summary
            </h4>

            <p>
                ${escapeHtml(
                    result.summary
                )}
            </p>


            <h4>
                Key Points
            </h4>

            <ul>

                ${result.key_points
                    .map(
                        point =>
                            `<li>
                                ${escapeHtml(
                                    point
                                )}
                            </li>`
                    )
                    .join("")}

            </ul>

            `
        );

    }

    catch (error) {

        showResult(
            "summaryResult",
            `
            <strong>
                Error
            </strong>

            <p>
                ${escapeHtml(
                    error.message
                )}
            </p>
            `
        );

    }

}


// =====================================================
// Health check
// =====================================================

async function checkHealth() {

    try {

        const response =
            await fetch(
                "/api/health"
            );


        const result =
            await response.json();


        if (
            result.gemini_configured
        ) {

            $("status").textContent =
                "Gemini connected";

        }

        else {

            $("status").textContent =
                "Demo mode";

        }

    }

    catch {

        $("status").textContent =
            "API unavailable";

    }

}


// Run health check
checkHealth();