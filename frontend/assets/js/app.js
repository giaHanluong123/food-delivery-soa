function showDemoMessage(pageName) {
    console.log("Current page:", pageName);
}

function setDemoRole(role) {
    localStorage.setItem("demo_role", role);
}

function getDemoRole() {
    return localStorage.getItem("demo_role");
}

function logoutDemo() {
    localStorage.removeItem("demo_role");
    localStorage.removeItem("access_token");
    window.location.href = "../index.html";
}