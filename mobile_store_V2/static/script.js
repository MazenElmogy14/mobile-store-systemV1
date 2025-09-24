document.addEventListener('DOMContentLoaded', function () {
    const quantityInput = document.getElementById('quantity');
    const serialInputsContainer = document.getElementById('serial-inputs');
    const addForm = document.getElementById('add-phone-form');
    const scannerDiv = document.getElementById('barcode-scanner');
    const closeScannerBtn = document.getElementById('close-scanner');

    let isScanning = false;
    let currentScanningInput = null;

    function startScanner(inputElement) {
        if (isScanning) stopScanner();

        scannerDiv.style.display = 'block';
        closeScannerBtn.style.display = 'block';
        currentScanningInput = inputElement;
        isScanning = true;

        Quagga.init({
            inputStream: {
                type: "LiveStream",
                target: scannerDiv,
                constraints: { facingMode: "environment" }
            },
            decoder: {
                readers: ["code_128_reader", "ean_reader", "upc_reader"]
            }
        }, function(err) {
            if (err) {
                console.error(err);
                alert("Camera init error: " + err);
                stopScanner();
                return;
            }
            Quagga.start();
        });

        Quagga.onDetected(function(result) {
            if (currentScanningInput) {
                currentScanningInput.value = result.codeResult.code;
                stopScanner();
            }
        });
    }

    function stopScanner() {
        if (isScanning) {
            Quagga.stop();
            scannerDiv.style.display = 'none';
            closeScannerBtn.style.display = 'none';
            currentScanningInput = null;
            isScanning = false;
        }
    }

    function generateSerialInputs() {
        const quantity = parseInt(quantityInput.value) || 0;
        serialInputsContainer.innerHTML = '';
        stopScanner();

        if (quantity > 0) {
            for (let i = 0; i < quantity; i++) {
                const div = document.createElement('div');
                div.className = 'col-md-6';
                div.innerHTML = `
                    <label for="serial-${i}" class="form-label">Serial Number #${i + 1}</label>
                    <div class="input-group">
                        <input type="text" class="form-control" id="serial-${i}" name="serials" placeholder="Enter or scan serial" required>
                        <button type="button" class="btn btn-outline-primary scan-btn" data-target-id="serial-${i}">📷 Scan</button>
                    </div>
                `;
                serialInputsContainer.appendChild(div);
            }
        }
    }

    addForm.addEventListener('submit', function(event) {
        const serialInputs = document.querySelectorAll('input[name="serials"]');
        const serialNumbers = Array.from(serialInputs).map(input => input.value.trim());
        const uniqueSerials = new Set(serialNumbers);

        if (uniqueSerials.size !== serialInputs.length) {
            event.preventDefault();
            alert('⚠️ All serial numbers must be unique!');
        }
    });

    serialInputsContainer.addEventListener('click', function(event) {
        if (event.target.classList.contains('scan-btn')) {
            const targetId = event.target.getAttribute('data-target-id');
            const targetInput = document.getElementById(targetId);
            startScanner(targetInput);
        }
    });

    closeScannerBtn.addEventListener('click', stopScanner);
    quantityInput.addEventListener('input', generateSerialInputs);
    quantityInput.addEventListener('change', generateSerialInputs);
});