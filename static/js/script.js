document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Delete Confirmation
    // Prevents accidental deletion of expenses
    const deleteLinks = document.querySelectorAll('.text-danger');
    
    deleteLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const confirmed = confirm("Are you sure you want to delete this expense?");
            if (!confirmed) {
                e.preventDefault(); // Stops the link from following the URL
            }
        });
    });

    // 2. Dynamic Date Setter
    // Automatically sets the date picker to today's date for convenience
    const dateInput = document.querySelector('input[type="date"]');
    if (dateInput && !dateInput.value) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }

    // 3. Auto-hide Flash Messages
    // Makes alert messages disappear after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // 4. Form Validation (Frontend)
    const expenseForm = document.querySelector('form[action="/add_expense"]');
    if (expenseForm) {
        expenseForm.addEventListener('submit', (e) => {
            const amount = expenseForm.querySelector('input[name="amount"]').value;
            if (parseFloat(amount) <= 0) {
                alert("Please enter an amount greater than 0.");
                e.preventDefault();
            }
        });
    }
});