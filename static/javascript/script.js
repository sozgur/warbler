$(".liked-icon .fa-heart").on("click", toggleLike);

async function toggleLike(e) {
    const heartIcon = $(e.target);
    const messageId = heartIcon.closest("div").data("id");
    const res = await axios({
        url: `/users/toggle_like/${messageId}`,
        method: "POST",
    });

    if (res.status === 200) {
        if (heartIcon.hasClass("liked")) {
            heartIcon.removeClass(["liked", "fas"]);
            heartIcon.addClass(["unliked", "far"]);
        } else if (heartIcon.hasClass("unliked")) {
            heartIcon.removeClass(["unliked", "far"]);
            heartIcon.addClass(["liked", "fas"]);
        }

        const totalLikes = res.data["total-likes"];
        $("a#like-count").text(totalLikes);
    }
}
