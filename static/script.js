const modal = document.getElementById('new_transaction');
const create_btn = document.getElementById('create_btn');

create_btn.addEventListener('click', () => {
    modal.style.display = 'flex';
})


function closeModal() {
    modal.style.display = 'none';
}

function submitTransaction() {
    // const name = document.getElementById('name').value;
    // const amount = document.getElementById('amount').value;
    // const category = document.getElementById('category').value;
    
    // alert(`Transaction Created: ${name}, $${amount}, ${category}`);
    closeModal();
}
