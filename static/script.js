const modal = document.getElementById('new_transaction');
const create_btn = document.getElementById('create_btn');

create_btn.addEventListener('click', () => {
    modal.style.display = 'flex';
})


function closeModal() {
    modal.style.display = 'none';
}

function submitTransaction() {
    closeModal();
}


// const editModal = document.getElementById('edit_transaction')
// const edit_btn = document.getElementById('edit-transaction-btn')

// edit_btn.addEventListener('click', () => {
//     editModal.style.display = 'flex';
// })

// function closeEditModal() {
//     editModal.style.display = 'none';
// }

// function submitEdit() {
//     closeEditModal();
// }

function openEditModal(button) {
    const edit_modal = document.getElementById('edit_transaction');
    edit_modal.style.display = 'flex';
    const form = document.getElementById('edit-transaction-form');
    
    const transactionId = button.getAttribute('data-transaction-id');
    const transactionStatus = button.getAttribute('data-transaction-status');
    const transactionCategory = button.getAttribute('data-transaction-category');
    const transactionName = button.getAttribute('data-transaction-name');
    const transactionDescription = button.getAttribute('data-transaction-description');
    const transactionAmount = button.getAttribute('data-transaction-amount');


    document.getElementById('edit-transaction-id').value = transactionId;
    document.getElementById('edit-status').value = transactionStatus;
    document.getElementById('edit-category').value = transactionCategory;
    document.getElementById('edit-name').value = transactionName;
    document.getElementById('edit-description').value = transactionDescription;
    document.getElementById('edit-amount').value = transactionAmount;
    
    form.action = `/edit_transaction/${transactionId}`;

}

function closeDeleteModal() {
    document.getElementById("confirm").style.display = "none";
}


function deleteModal(button) {
    const transactionId = button.getAttribute('data-transaction-id');

    document.getElementById("confirm").style.display = 'block';

    document.getElementById("confirmDeleteBtn").onclick = function() {
        fetch(`delete_transaction/${transactionId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        
        .then(data => {
            location.reload();
        })
        // form.action = `/delete_transaction/${transactionId}`;
        closeDeleteModal();
    }
}

// function closeEditModal() {
//     const edit_modal = document.getElementById('edit-transaction-modal');
//     edit_modal.style.display = 'none';
// }