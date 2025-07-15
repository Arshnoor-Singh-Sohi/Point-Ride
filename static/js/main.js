// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Password Strength and Match Validation ---
    const passwordInput = document.getElementById('id_password');
    const password2Input = document.getElementById('id_password2');
    const passwordStrengthFeedback = document.getElementById('password-strength-feedback');
    const passwordMatchFeedback = document.getElementById('password-match-feedback');

    // Function to check password strength
    function checkPasswordStrength(password) {
        let strength = 0;
        let feedback = '';

        if (password.length >= 8) {
            strength += 1;
        } else {
            feedback += 'Must be at least 8 characters long. ';
        }
        if (password.match(/[a-z]/)) {
            strength += 1;
        } else {
            feedback += 'Must contain a lowercase letter. ';
        }
        if (password.match(/[A-Z]/)) {
            strength += 1;
        } else {
            feedback += 'Must contain an uppercase letter. ';
        }
        if (password.match(/[0-9]/)) {
            strength += 1;
        } else {
            feedback += 'Must contain a number. ';
        }
        if (password.match(/[^a-zA-Z0-9]/)) {
            strength += 1;
        } else {
            feedback += 'Must contain a special character. ';
        }

        let strengthText = '';
        let textColorClass = '';

        if (password.length === 0) {
            strengthText = '';
            feedback = '';
            textColorClass = '';
        } else if (strength < 3) {
            strengthText = 'Weak';
            textColorClass = 'text-danger';
        } else if (strength === 3) {
            strengthText = 'Moderate';
            textColorClass = 'text-warning';
        } else {
            strengthText = 'Strong';
            textColorClass = 'text-success';
        }

        passwordStrengthFeedback.innerHTML = `<span class="${textColorClass}">${strengthText}</span> ${feedback}`;
    }

    // Function to check if passwords match
    function checkPasswordMatch() {
        if (!passwordInput || !password2Input || !passwordMatchFeedback) return;

        const password = passwordInput.value;
        const password2 = password2Input.value;

        if (password2.length > 0) {
            if (password === password2) {
                passwordMatchFeedback.innerHTML = '<span class="text-success">Passwords match!</span>';
            } else {
                passwordMatchFeedback.innerHTML = '<span class="text-danger">Passwords do not match.</span>';
            }
        } else {
            passwordMatchFeedback.innerHTML = '';
        }
    }

    // Event listeners for password fields
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            checkPasswordStrength(this.value);
            checkPasswordMatch();
        });
    }
    if (password2Input) {
        password2Input.addEventListener('input', checkPasswordMatch);
    }

    // --- General Form Submission Handling (for required fields, etc.) ---
    // This part is more about enhancing default browser validation feedback
    // and ensuring a smooth user experience. Django's server-side validation
    // will always be the ultimate source of truth.

    const forms = document.querySelectorAll('form'); // Get all forms on the page

    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            // Check HTML5 validity
            if (!form.checkValidity()) {
                event.preventDefault(); // Prevent default submission if form is invalid
                event.stopPropagation(); // Stop propagation

                // Add Bootstrap's 'was-validated' class to show validation feedback
                form.classList.add('was-validated');

                // You could also add a custom "missing info" popup here if desired,
                // but Bootstrap's invalid-feedback is usually sufficient.
                // Example for a simple message box (replace with a custom modal if preferred):
                // const firstInvalidField = form.querySelector(':invalid');
                // if (firstInvalidField) {
                //     // For a real app, use a custom modal or toast notification
                //     console.log("Please fill out all required fields correctly.");
                //     // alert("Please fill out all required fields correctly."); // Avoid alert()
                // }
            }
        }, false); // Use capture phase to ensure it runs before default submission
    });

    // Add 'is-invalid' class to fields with server-side errors on page load
    // This ensures that if the form reloads due to server-side validation failures,
    // the Bootstrap error styling is applied immediately.
    document.querySelectorAll('.invalid-feedback.d-block').forEach(errorDiv => {
        const fieldContainer = errorDiv.closest('.mb-3');
        if (fieldContainer) {
            const inputField = fieldContainer.querySelector('input, select, textarea');
            if (inputField) {
                inputField.classList.add('is-invalid');
            }
        }
    });
});
