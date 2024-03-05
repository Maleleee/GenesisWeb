const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

registerBtn.addEventListener('click', () => {
    container.classList.add("active");
});

loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
});

// function.js

// Logic for redirection after successful sign-in on signuplogin.html
document.querySelector('.sign-in form').addEventListener('submit', function(event) {
    // Prevent the default form submission
    event.preventDefault();

    // Redirect to the user dashboard page after successful sign-in
    window.location.href = 'userdash.html';
});
