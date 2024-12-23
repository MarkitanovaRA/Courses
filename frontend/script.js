const apiBaseUrl = "http://127.0.0.1:5000";

// Форма входа
const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await fetch(`${apiBaseUrl}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (response.ok) {
      alert("Login successful!");
      localStorage.setItem("user_id", data.user_id);
      localStorage.setItem("role", data.role);  // Сохраняем роль для дальнейшего использования

      // Переход на страницу курсов
      if (data.role === "teacher") {
        window.location.href = "courses.html";  // Для учителя, перенаправляем на страницу курсов
      } else {
        // В будущем можно добавить редирект для других ролей (например, ученика)
        window.location.href = "student_dashboard.html";  // Для ученика, перенаправляем на его страницу
      }
    } else {
      alert(data.message || "Error logging in");
    }
  });
}

// Форма регистрации
const registerForm = document.getElementById("register-form");
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const role = document.getElementById("role").value;

    const response = await fetch(`${apiBaseUrl}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password, role }),
    });

    if (response.ok) {
      alert("Registration successful!");
      window.location.href = "login.html";
    } else {
      alert("Error during registration");
    }
  });
}

// Загрузка списка курсов
const coursesList = document.getElementById("courses-list");
if (coursesList) {
  window.onload = async () => {
    const response = await fetch(`${apiBaseUrl}/courses`);
    const courses = await response.json();
    courses.forEach((course) => {
      const li = document.createElement("li");
      li.innerHTML = `<a href="course-details.html?id=${course.id}">${course.title}</a>`;
      coursesList.appendChild(li);
    });
  };
}
