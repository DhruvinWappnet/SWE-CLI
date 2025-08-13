document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const switchToSignupLink = document.getElementById('switchToSignup');
    const switchToLoginLink = document.getElementById('switchToLogin');

    if (switchToSignupLink) {
        switchToSignupLink.addEventListener('click', (e) => {
            e.preventDefault();
            if (loginForm) loginForm.style.transform = 'translateX(-100%)';
            if (signupForm) signupForm.style.transform = 'translateX(0)';
        });
    }

    if (switchToLoginLink) {
        switchToLoginLink.addEventListener('click', (e) => {
            e.preventDefault();
            if (loginForm) loginForm.style.transform = 'translateX(0)';
            if (signupForm) signupForm.style.transform = 'translateX(100%)';
        });
    }

    // Basic form validation (example for login)
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = loginForm.querySelector('input[type="text"]').value;
            const password = loginForm.querySelector('input[type="password"]').value;

            if (username === '' || password === '') {
                alert('Please fill in all fields.');
            } else {
                alert('Login successful!');
                // In a real application, you would send data to a server
            }
        });
    }

    // Basic form validation (example for signup)
    if (signupForm) {
        signupForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = signupForm.querySelector('input[type="text"]').value;
            const email = signupForm.querySelector('input[type="email"]').value;
            const password = signupForm.querySelector('input[type="password"]').value;
            const confirmPassword = signupForm.querySelector('input[placeholder="Confirm Password"]').value;

            if (username === '' || email === '' || password === '' || confirmPassword === '') {
                alert('Please fill in all fields.');
            } else if (password !== confirmPassword) {
                alert('Passwords do not match.');
            } else {
                alert('Sign up successful!');
                // In a real application, you would send data to a server
            }
        });
    }
});
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const switchToSignupLink = document.getElementById('switchToSignup');
    const switchToLoginLink = document.getElementById('switchToLogin');

    if (switchToSignupLink) {
        switchToSignupLink.addEventListener('click', (e) => {
            e.preventDefault();
            if (loginForm) loginForm.style.transform = 'translateX(-100%)';
            if (signupForm) signupForm.style.transform = 'translateX(0)';
        });
    }

    if (switchToLoginLink) {
        switchToLoginLink.addEventListener('click', (e) => {
            e.preventDefault();
            if (loginForm) loginForm.style.transform = 'translateX(0)';
            if (signupForm) signupForm.style.transform = 'translateX(100%)';
        });
    }

    // Basic form validation (example for login)
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = loginForm.querySelector('input[type="text"]').value;
            const password = loginForm.querySelector('input[type="password"]').value;

            if (username === '' || password === '') {
                alert('Please fill in all fields.');
            } else {
                alert('Login successful!');
                // In a real application, you would send data to a server
            }
        });
    }

    // Basic form validation (example for signup)
    if (signupForm) {
        signupForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = signupForm.querySelector('input[type="text"]').value;
            const email = signupForm.querySelector('input[type="email"]').value;
            const password = signupForm.querySelector('input[type="password"]').value;
            const confirmPassword = signupForm.querySelector('input[placeholder="Confirm Password"]').value;

            if (username === '' || email === '' || password === '' || confirmPassword === '') {
                alert('Please fill in all fields.');
            } else if (password !== confirmPassword) {
                alert('Passwords do not match.');
            } else {
                alert('Sign up successful!');
                // In a real application, you would send data to a server
            }
        });
    }
});


