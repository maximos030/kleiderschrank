$(document).ready(function () {
    let tops = [];
    let bottoms = [];
    let shoes = [];

    function loadImages(category, callback) {
        $.getJSON(`/get_images/${category}`, function (data) {
            callback(data);
        });
    }

    loadImages('top', function (data) {
        tops = data;
        displayCurrentItems();
    });

    loadImages('bottom', function (data) {
        bottoms = data;
        displayCurrentItems();
    });

    loadImages('shoe', function (data) {
        shoes = data;
        displayCurrentItems();
    });

    let currentTopIndex = 0;
    let currentBottomIndex = 0;
    let currentShoeIndex = 0;

    function displayItem(items, containerId, index) {
        const item = items[index];
        $(`#${containerId}`).html(`
            <img src="${item.src}" alt="${item.alt}">
        `);
    }

    function displayCurrentItems() {
        if (tops.length > 0) {
            displayItem(tops, 'tops', currentTopIndex);
        }
        if (bottoms.length > 0) {
            displayItem(bottoms, 'bottoms', currentBottomIndex);
        }
        if (shoes.length > 0) {
            displayItem(shoes, 'shoes', currentShoeIndex);
        }
    }

    $('#prev-top').click(function () {
        currentTopIndex = (currentTopIndex > 0) ? currentTopIndex - 1 : tops.length - 1;
        displayItem(tops, 'tops', currentTopIndex);
    });

    $('#next-top').click(function () {
        currentTopIndex = (currentTopIndex < tops.length - 1) ? currentTopIndex + 1 : 0;
        displayItem(tops, 'tops', currentTopIndex);
    });

    $('#prev-bottom').click(function () {
        currentBottomIndex = (currentBottomIndex > 0) ? currentBottomIndex - 1 : bottoms.length - 1;
        displayItem(bottoms, 'bottoms', currentBottomIndex);
    });

    $('#next-bottom').click(function () {
        currentBottomIndex = (currentBottomIndex < bottoms.length - 1) ? currentBottomIndex + 1 : 0;
        displayItem(bottoms, 'bottoms', currentBottomIndex);
    });

    $('#prev-shoe').click(function () {
        currentShoeIndex = (currentShoeIndex > 0) ? currentShoeIndex - 1 : shoes.length - 1;
        displayItem(shoes, 'shoes', currentShoeIndex);
    });

    $('#next-shoe').click(function () {
        currentShoeIndex = (currentShoeIndex < shoes.length - 1) ? currentShoeIndex + 1 : 0;
        displayItem(shoes, 'shoes', currentShoeIndex);
    });

    $('#save-outfit').click(function () {
        const topImage = tops[currentTopIndex].src;
        const bottomImage = bottoms[currentBottomIndex].src;
        const shoeImage = shoes[currentShoeIndex].src;

        const outfitCanvas = document.createElement('canvas');
        const context = outfitCanvas.getContext('2d');
        const canvasWidth = 300;  // Adjust as needed
        const canvasHeight = 900; // Adjust as needed

        outfitCanvas.width = canvasWidth;
        outfitCanvas.height = canvasHeight;

        const topImg = new Image();
        const bottomImg = new Image();
        const shoeImg = new Image();

        topImg.src = topImage;
        bottomImg.src = bottomImage;
        shoeImg.src = shoeImage;

        topImg.onload = () => {
            context.drawImage(topImg, 0, 0, canvasWidth, canvasHeight / 3);
            bottomImg.onload = () => {
                context.drawImage(bottomImg, 0, canvasHeight / 3, canvasWidth, canvasHeight / 3);
                shoeImg.onload = () => {
                    context.drawImage(shoeImg, 0, (2 * canvasHeight) / 3, canvasWidth, canvasHeight / 3);
                    const link = document.createElement('a');
                    link.download = 'outfit.png';
                    link.href = outfitCanvas.toDataURL();
                    link.click();
                };
            };
        };
    });
});
