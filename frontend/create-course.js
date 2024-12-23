document.addEventListener("DOMContentLoaded", () => {
    let moduleCount = 0;
    let lessonCount = 0;
    let testCount = 0;

    // Делегирование событий для всех кнопок в контейнере #modules
    document.getElementById("modules").addEventListener("click", (event) => {
        // Обработчик для кнопки "Add Module"
        if (event.target.id === "add-module") {
            moduleCount++;
            const moduleDiv = document.createElement("div");
            moduleDiv.classList.add("module");
            moduleDiv.setAttribute("data-module-id", moduleCount);

            moduleDiv.innerHTML = `
                <input type="text" class="module-title" placeholder="Module Title" required>
                <input type="number" class="module-order" placeholder="Module Order" required>
                <button class="add-lesson add-button">Add Lesson</button>
                <div class="lessons"></div>
                <button class="add-test add-button">Add Test</button>
                <div class="tests"></div>
            `;

            document.getElementById("modules").appendChild(moduleDiv);
        }

        // Обработчик для кнопки "Add Lesson"
        if (event.target.classList.contains("add-lesson")) {
            lessonCount++;
            const moduleDiv = event.target.closest(".module");
            const lessonDiv = document.createElement("div");
            lessonDiv.classList.add("lesson");
            lessonDiv.setAttribute("data-lesson-id", lessonCount);

            lessonDiv.innerHTML = `
                <input type="text" class="lesson-title" placeholder="Lesson Title" required>
                <textarea class="lesson-content" placeholder="Lesson Content" required></textarea>
                <input type="text" class="lesson-media-type" placeholder="Media Type (e.g., video, image)" required>
                <input type="text" class="lesson-media-url" placeholder="Media URL" required>
                <input type="number" class="lesson-order" placeholder="Lesson Order" required>
                <button class="remove-lesson">Remove Lesson</button>
            `;

            lessonDiv.querySelector(".remove-lesson").addEventListener("click", () => {
                lessonDiv.remove();
            });

            moduleDiv.querySelector(".lessons").appendChild(lessonDiv);
        }

        // Обработчик для кнопки "Add Test"
        if (event.target.classList.contains("add-test")) {
            testCount++;
            const moduleDiv = event.target.closest(".module");
            const testDiv = document.createElement("div");
            testDiv.classList.add("test");
            testDiv.setAttribute("data-test-id", testCount);

            testDiv.innerHTML = `
                <input type="text" class="test-title" placeholder="Test Title" required>
                <textarea class="test-json" placeholder='Enter test as JSON (e.g., [{"question": "Q1", "answers": [...], "correct_answer": "..."}])' required></textarea>
                <button class="remove-test">Remove Test</button>
            `;

            testDiv.querySelector(".remove-test").addEventListener("click", () => {
                testDiv.remove();
            });

            moduleDiv.querySelector(".tests").appendChild(testDiv);
        }
    });

    // Отправка формы для создания курса
    document.getElementById("create-course").addEventListener("click", async () => {
        const courseTitle = document.getElementById("course-title").value;
        const courseDescription = document.getElementById("course-description").value;

        const modules = [];

        document.querySelectorAll(".module").forEach((moduleDiv) => {
            const moduleTitle = moduleDiv.querySelector(".module-title").value;
            const moduleOrder = moduleDiv.querySelector(".module-order").value;

            const lessons = [];
            moduleDiv.querySelectorAll(".lesson").forEach((lessonDiv) => {
                lessons.push({
                    title: lessonDiv.querySelector(".lesson-title").value,
                    content: lessonDiv.querySelector(".lesson-content").value,
                    mediaType: lessonDiv.querySelector(".lesson-media-type").value,
                    mediaUrl: lessonDiv.querySelector(".lesson-media-url").value,
                    order: lessonDiv.querySelector(".lesson-order").value,
                });
            });

            const tests = [];
            moduleDiv.querySelectorAll(".test").forEach((testDiv) => {
                const testTitle = testDiv.querySelector(".test-title").value;
                const testJSON = testDiv.querySelector(".test-json").value;

                try {
                    const parsedTest = JSON.parse(testJSON);
                    tests.push({
                        title: testTitle,
                        questions: parsedTest,
                    });
                } catch (error) {
                    alert("Invalid JSON format in test: " + testTitle);
                    throw error;
                }
            });

            modules.push({
                title: moduleTitle,
                order: moduleOrder,
                lessons: lessons,
                tests: tests,
            });
        });

        const courseData = {
            title: courseTitle,
            description: courseDescription,
            modules: modules,
        };

        try {
            const response = await fetch("http://localhost:5000/create_course", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(courseData),
            });

            const result = await response.json();

            if (response.ok) {
                alert("Course created successfully!");
                console.log(result);
            } else {
                alert("Error creating course: " + result.message);
            }
        } catch (error) {
            console.error("Error:", error);
        }
    });
});
document.getElementById("generate-qr-code").addEventListener("click", async () => {
    const courseTitle = document.getElementById("course-title").value.trim();
    const courseDescription = document.getElementById("course-description").value.trim();

    if (!courseTitle || !courseDescription) {
        alert("Please fill out the course title and description.");
        return;
    }

    const apiUrl = "http://localhost:5000/generate_qr";

    const requestData = {
        title: courseTitle,
        description: courseDescription
    };

    try {
        const response = await fetch(apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestData)
        });

        // Проверяем, был ли успешный ответ от API
        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        const result = await response.json();

        // Убедитесь, что результат имеет нужный формат
        if (!result.qr_code_path) {
            throw new Error("QR code data is missing in the response.");
        }

        // Создание ссылки для скачивания
        const downloadUrl = `http://localhost:5000/download_qr/${courseTitle}.png`;

        // Инициализация скачивания
        const link = document.createElement("a");
        link.href = downloadUrl;
        link.download = `${courseTitle}.png`;  // Название файла для скачивания
        link.click();

        alert("QR code generated and ready for download!");

    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred while generating the QR code.");
    }
});

