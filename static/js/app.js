/* SHOWTIME APP - FRONTEND APPLICATION ENGINE */

const app = {
    state: {
        city: { id: 1, name: "Mumbai" },
        movies: [],
        trendingMovies: [],
        cities: [],
        selectedMovie: null,
        selectedShowtime: null,
        selectedDate: null,
        selectedSeats: [], // [{seat_code, tier, price}]
        selectedFnB: {},   // { item_id: qty }
        fnbCatalog: [],
        appliedPromo: null,
        userEmail: "rahul@example.com",
        currentUser: JSON.parse(localStorage.getItem("showtime_user") || "null"),
        authMode: "login",
        activeLanguageFilter: "All",
        activeGenreFilter: "All",
        activeCategory: "movies",
        watchlist: JSON.parse(localStorage.getItem("showtime_watchlist") || "[]"),
        currentBannerIndex: 0,
        bannerTimer: null
    },

    init: async function() {
        this.updateAuthUI();
        this.updateWatchlistBadge();
        await this.loadCities();
        await this.loadMovies();
        await this.loadFnBCatalog();
        this.renderCarousel();
        this.renderMovieGrid();
        this.setupSearchClickListener();

        // ALWAYS OPEN LOGIN MODAL FIRST ON PAGE LOAD AS REQUESTED!
        setTimeout(() => {
            this.openLoginModal();
        }, 200);
    },

    setupSearchClickListener: function() {
        document.addEventListener("click", (e) => {
            const searchBox = document.querySelector(".search-box");
            const dropdown = document.getElementById("searchResultsDropdown");
            if (searchBox && dropdown && !searchBox.contains(e.target)) {
                dropdown.classList.remove("active");
            }
        });
    },

    // ---------------- AUTHENTICATION & LOGIN ---------------- //

    updateAuthUI: function() {
        const btnLabel = document.getElementById("authBtnLabel");
        const btn = document.getElementById("authNavBtn");
        if (this.state.currentUser) {
            btnLabel.innerText = this.state.currentUser.name;
            if (btn) btn.style.borderColor = "var(--primary)";
            this.state.userEmail = this.state.currentUser.email;
        } else {
            btnLabel.innerText = "Sign In";
            if (btn) btn.style.borderColor = "var(--cyan)";
        }
    },

    openLoginModal: function() {
        const formContainer = document.getElementById("authFormContainer");
        const profileContainer = document.getElementById("userProfileContainer");

        if (this.state.currentUser) {
            formContainer.style.display = "none";
            profileContainer.style.display = "block";

            document.getElementById("userAvatar").innerText = this.state.currentUser.name.charAt(0).toUpperCase();
            document.getElementById("userProfileName").innerText = this.state.currentUser.name;
            document.getElementById("userProfileEmail").innerText = this.state.currentUser.email;
            document.getElementById("userWatchlistCount").innerText = this.state.watchlist.length;
            document.getElementById("userBookingsCount").innerText = "1";
        } else {
            formContainer.style.display = "block";
            profileContainer.style.display = "none";
            this.switchAuthTab("login");
        }

        this.openModal("loginModal");
    },

    switchAuthTab: function(mode) {
        this.state.authMode = mode;
        const btnSignIn = document.getElementById("tabSignIn");
        const btnSignUp = document.getElementById("tabSignUp");
        const nameGroup = document.getElementById("nameFieldGroup");
        const submitText = document.getElementById("authSubmitText");
        const errDiv = document.getElementById("authErrorMsg");
        errDiv.innerText = "";

        if (mode === "login") {
            btnSignIn.style.background = "var(--primary)";
            btnSignIn.style.color = "#fff";
            btnSignUp.style.background = "transparent";
            btnSignUp.style.color = "var(--text-muted)";
            nameGroup.style.display = "none";
            submitText.innerText = "Sign In to ShowTime";
        } else {
            btnSignUp.style.background = "var(--primary)";
            btnSignUp.style.color = "#fff";
            btnSignIn.style.background = "transparent";
            btnSignIn.style.color = "var(--text-muted)";
            nameGroup.style.display = "block";
            submitText.innerText = "Create Free Account";
        }
    },

    handleAuthSubmit: async function(e) {
        e.preventDefault();
        const errDiv = document.getElementById("authErrorMsg");
        errDiv.innerText = "";

        const email = document.getElementById("authEmail").value.trim();
        const password = document.getElementById("authPassword").value.trim();
        const name = document.getElementById("authName").value.trim();

        const endpoint = this.state.authMode === "login" ? "/api/auth/login" : "/api/auth/register";
        const payload = this.state.authMode === "login" ? { email, password } : { name, email, password };

        try {
            const res = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (res.ok && data.success) {
                this.state.currentUser = data.user;
                localStorage.setItem("showtime_user", JSON.stringify(data.user));
                localStorage.setItem("showtime_token", data.token);
                this.updateAuthUI();
                this.closeModal("loginModal");
                alert(`✨ ${data.message}`);
            } else {
                errDiv.innerText = data.detail || "Authentication failed!";
            }
        } catch (err) {
            errDiv.innerText = "Network error signing in!";
        }
    },

    logoutUser: function() {
        this.state.currentUser = null;
        localStorage.removeItem("showtime_user");
        localStorage.removeItem("showtime_token");
        this.updateAuthUI();
        this.closeModal("loginModal");
    },

    // ---------------- AI ASSISTANT CHAT WIDGET ---------------- //

    toggleAiChat: function() {
        const box = document.getElementById("aiChatBox");
        if (box) {
            box.style.display = box.style.display === "none" ? "block" : "none";
        }
    },

    sendAiQuery: async function() {
        const input = document.getElementById("aiInput");
        const logs = document.getElementById("aiChatLogs");
        const query = input.value.trim();
        if (!query) return;

        const userDiv = document.createElement("div");
        userDiv.style.background = "rgba(244, 63, 94, 0.2)";
        userDiv.style.padding = "0.5rem 0.75rem";
        userDiv.style.borderRadius = "10px";
        userDiv.style.alignSelf = "flex-end";
        userDiv.innerText = query;
        logs.appendChild(userDiv);
        input.value = "";
        logs.scrollTop = logs.scrollHeight;

        try {
            const res = await fetch("/api/ai/recommend", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: query })
            });
            const data = await res.json();

            const botDiv = document.createElement("div");
            botDiv.style.background = "rgba(255, 255, 255, 0.06)";
            botDiv.style.padding = "0.5rem 0.75rem";
            botDiv.style.borderRadius = "10px";
            botDiv.innerHTML = data.reply.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            logs.appendChild(botDiv);
            logs.scrollTop = logs.scrollHeight;
        } catch (e) {
            console.error("AI Error", e);
        }
    },

    // ---------------- WATCHLIST SYSTEM ---------------- //

    toggleWatchlist: function(movieId, e) {
        if (e) {
            e.stopPropagation();
            e.preventDefault();
        }
        const idx = this.state.watchlist.indexOf(movieId);
        if (idx > -1) {
            this.state.watchlist.splice(idx, 1);
        } else {
            this.state.watchlist.push(movieId);
        }
        localStorage.setItem("showtime_watchlist", JSON.stringify(this.state.watchlist));
        this.updateWatchlistBadge();
        this.renderMovieGrid();
    },

    updateWatchlistBadge: function() {
        const badge = document.getElementById("watchlistCount");
        if (badge) badge.innerText = this.state.watchlist.length;
    },

    openWatchlistModal: function() {
        const grid = document.getElementById("watchlistGrid");
        if (!grid) return;
        grid.innerHTML = "";

        const savedMovies = this.state.movies.filter(m => this.state.watchlist.includes(m.id));
        if (savedMovies.length === 0) {
            grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-muted);">
                <i class="fa-regular fa-heart" style="font-size: 2.5rem; margin-bottom: 1rem; color: var(--primary);"></i>
                <h4>Your watchlist is empty</h4>
                <p>Click the heart icon on any movie to save it for later!</p>
            </div>`;
        } else {
            savedMovies.forEach(m => {
                const card = document.createElement("div");
                card.className = "movie-card";
                card.onclick = () => {
                    this.closeModal("watchlistModal");
                    this.openMovieDetail(m.id);
                };
                card.innerHTML = `
                    <div class="poster-wrapper">
                        <img src="${m.poster_url}" class="poster-img" alt="${m.title}">
                    </div>
                    <div class="card-info">
                        <div class="card-title">${m.title}</div>
                        <button class="btn-book-quick">Book Now</button>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        this.openModal("watchlistModal");
    },

    // ---------------- SMART SEAT PICKER ---------------- //

    smartAutoSelectSeats: function(count) {
        if (!this.state.selectedShowtime) return;

        this.state.selectedSeats = [];
        document.querySelectorAll("#seatingArea .seat").forEach(s => s.classList.remove("selected"));

        const seats = Array.from(document.querySelectorAll("#seatingArea .seat:not(.reserved)"));
        const preferredRows = ["D", "E", "C", "B", "F"];

        let picked = [];
        for (let rowLabel of preferredRows) {
            const rowSeats = seats.filter(s => s.dataset.code.startsWith(rowLabel));
            if (rowSeats.length >= count) {
                const mid = Math.floor(rowSeats.length / 2);
                picked = rowSeats.slice(Math.max(0, mid - Math.floor(count / 2)), Math.max(0, mid - Math.floor(count / 2)) + count);
                break;
            }
        }

        if (picked.length < count && seats.length >= count) {
            picked = seats.slice(0, count);
        }

        picked.forEach(seatEl => {
            seatEl.classList.add("selected");
            this.state.selectedSeats.push({
                seat_code: seatEl.dataset.code,
                tier: seatEl.dataset.tier,
                price: parseFloat(seatEl.dataset.price)
            });
        });

        this.updateSeatCartUI();
    },

    // ---------------- API FETCHERS ---------------- //

    loadCities: async function() {
        try {
            const res = await fetch("/api/cities");
            this.state.cities = await res.json();
            this.renderCityGrid();
        } catch (e) {
            console.error("Failed to load cities", e);
        }
    },

    loadMovies: async function() {
        try {
            let url = `/api/movies?city_id=${this.state.city.id}`;
            if (this.state.activeLanguageFilter !== "All") {
                url += `&language=${encodeURIComponent(this.state.activeLanguageFilter)}`;
            }
            if (this.state.activeGenreFilter !== "All") {
                url += `&genre=${encodeURIComponent(this.state.activeGenreFilter)}`;
            }

            const res = await fetch(url);
            this.state.movies = await res.json();

            if (this.state.movies.length === 0) {
                const resAll = await fetch(`/api/movies`);
                this.state.movies = await resAll.json();
            }
            
            this.state.trendingMovies = this.state.movies.filter(m => m.is_trending).slice(0, 4);
            if (this.state.trendingMovies.length === 0) {
                this.state.trendingMovies = this.state.movies.slice(0, 4);
            }
        } catch (e) {
            console.error("Failed to load movies", e);
        }
    },

    loadFnBCatalog: async function() {
        try {
            const res = await fetch("/api/food-beverages");
            this.state.fnbCatalog = await res.json();
        } catch (e) {
            console.error("Failed to load F&B catalog", e);
        }
    },

    // ---------------- ADMIN / EDIT MODE ---------------- //

    openAdminModal: function() {
        this.openModal("adminModal");
    },

    saveNewMovie: async function(e) {
        e.preventDefault();

        const title = document.getElementById("admTitle").value.trim();
        const lang = document.getElementById("admLang").value.trim();
        const genre = document.getElementById("admGenre").value.trim();
        const cert = document.getElementById("admCert").value.trim();
        const duration = parseInt(document.getElementById("admDuration").value);
        const synopsis = document.getElementById("admSynopsis").value.trim();
        const poster = document.getElementById("admPoster").value.trim();
        const backdrop = document.getElementById("admBackdrop").value.trim();
        const trailer = document.getElementById("admTrailer").value.trim();
        const director = document.getElementById("admDirector").value.trim();

        const payload = {
            title: title,
            language: lang,
            genre: genre,
            certificate: cert,
            duration_mins: duration,
            release_date: new Date().toISOString().split('T')[0],
            rating_percentage: 95,
            rating_count: 10000,
            likes_count: 25000,
            synopsis: synopsis,
            director: director,
            cast: [
                { name: "Lead Star", role: "Protagonist", avatar: "/static/images/cast/thalapathy_vijay.jpg" }
            ],
            poster_url: poster,
            backdrop_url: backdrop,
            trailer_url: trailer,
            formats: ["2D", "IMAX 3D"],
            is_trending: true
        };

        try {
            const res = await fetch("/api/admin/movies", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (res.ok && data.success) {
                alert(`✨ Success! ${data.message}`);
                this.closeModal("adminModal");
                await this.loadMovies();
                this.renderCarousel();
                this.renderMovieGrid();
            } else {
                alert("Failed to save movie!");
            }
        } catch (err) {
            console.error("Save movie error", err);
            alert("Error connecting to server!");
        }
    },

    deleteMovie: async function(movieId) {
        if (!confirm("Are you sure you want to delete this movie from the catalog?")) return;

        try {
            const res = await fetch(`/api/admin/movies/${movieId}`, { method: "DELETE" });
            const data = await res.json();
            if (res.ok && data.success) {
                this.closeModal("movieDetailModal");
                await this.loadMovies();
                this.renderCarousel();
                this.renderMovieGrid();
            }
        } catch (e) {
            console.error("Delete movie failed", e);
        }
    },

    // ---------------- CATEGORY SWITCHER ---------------- //

    switchCategory: function(cat, element, event) {
        if (event) event.preventDefault();
        this.state.activeCategory = cat;

        const links = element.parentElement.querySelectorAll("a");
        links.forEach(l => {
            l.style.color = "var(--text-muted)";
            l.classList.remove("active");
        });
        element.style.color = "var(--primary)";
        element.classList.add("active");

        const title = document.getElementById("catalogSectionTitle");
        if (cat === "events") title.innerText = "Trending Events & Comedy Shows";
        else if (cat === "sports") title.innerText = "Live Sports & IPL Matches";
        else if (cat === "plays") title.innerText = "Music Concerts & Theatre Plays";
        else title.innerText = "Now Showing Movies";

        this.renderMovieGrid();
    },

    // ---------------- HERO CAROUSEL ---------------- //

    renderCarousel: function() {
        const track = document.getElementById("bannerTrack");
        const dotsContainer = document.getElementById("carouselDots");
        if (!track || this.state.trendingMovies.length === 0) return;

        track.innerHTML = "";
        dotsContainer.innerHTML = "";

        this.state.trendingMovies.forEach((m, idx) => {
            const slide = document.createElement("div");
            slide.className = "banner-slide";
            slide.style.backgroundImage = `linear-gradient(90deg, rgba(10,12,20,0.95) 0%, rgba(10,12,20,0.7) 50%, rgba(10,12,20,0.95) 100%), url('${m.poster_url}')`;
            slide.style.backgroundSize = "cover";
            slide.style.backgroundPosition = "center";

            slide.innerHTML = `
                <div class="banner-content" style="display: flex; gap: 2rem; align-items: center; width: 100%; max-width: 1200px;">
                    <img src="${m.poster_url}" alt="${m.title}" style="width: 220px; height: 310px; object-fit: cover; border-radius: 18px; box-shadow: 0 15px 35px rgba(0,0,0,0.8); border: 2px solid var(--border-glass);">
                    <div style="flex: 1;">
                        <div class="banner-badge"><i class="fa-solid fa-fire"></i> Trending Blockbuster</div>
                        <h1 class="banner-title">${m.title}</h1>
                        <div class="banner-meta">
                            <span class="rating-chip"><i class="fa-solid fa-star"></i> ${m.rating_percentage}% (${(m.rating_count/1000).toFixed(0)}K votes)</span>
                            <span><i class="fa-solid fa-clock"></i> ${m.duration_mins} mins</span>
                            <span><i class="fa-solid fa-film"></i> ${m.language}</span>
                            <span style="border: 1px solid var(--border-glass); padding: 0.1rem 0.5rem; border-radius: 6px;">${m.certificate}</span>
                        </div>
                        <div class="banner-actions">
                            <button class="btn-primary" onclick="app.openMovieDetail(${m.id})">
                                <i class="fa-solid fa-ticket"></i> Book Tickets
                            </button>
                            <button class="btn-secondary" onclick="app.openTrailerModal('${m.trailer_url}')">
                                <i class="fa-solid fa-play"></i> Watch Trailer
                            </button>
                        </div>
                    </div>
                </div>
            `;
            track.appendChild(slide);

            const dot = document.createElement("div");
            dot.className = `dot ${idx === 0 ? 'active' : ''}`;
            dot.onclick = () => this.goToBanner(idx);
            dotsContainer.appendChild(dot);
        });

        if (this.state.bannerTimer) clearInterval(this.state.bannerTimer);
        this.state.bannerTimer = setInterval(() => {
            let nextIndex = (this.state.currentBannerIndex + 1) % this.state.trendingMovies.length;
            this.goToBanner(nextIndex);
        }, 5000);
    },

    goToBanner: function(index) {
        this.state.currentBannerIndex = index;
        const track = document.getElementById("bannerTrack");
        if (track) {
            track.style.transform = `translateX(-${index * 100}%)`;
        }
        const dots = document.querySelectorAll(".carousel-dots .dot");
        dots.forEach((d, i) => {
            d.classList.toggle("active", i === index);
        });
    },

    // ---------------- MOVIE GRID ---------------- //

    renderMovieGrid: function() {
        const grid = document.getElementById("movieGrid");
        if (!grid) return;
        grid.innerHTML = "";

        if (this.state.movies.length === 0) {
            grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 4rem; color: var(--text-muted);">
                <i class="fa-solid fa-film" style="font-size: 3rem; margin-bottom: 1rem; color: var(--primary);"></i>
                <h3>No items match your filters</h3>
                <p>Try switching language or genre filters.</p>
            </div>`;
            return;
        }

        this.state.movies.forEach(m => {
            const isFav = this.state.watchlist.includes(m.id);
            const card = document.createElement("div");
            card.className = "movie-card";
            card.onclick = () => this.openMovieDetail(m.id);

            card.innerHTML = `
                <div class="poster-wrapper">
                    <img src="${m.poster_url}" class="poster-img" alt="${m.title}" loading="lazy">
                    <div class="card-rating-badge">
                        <i class="fa-solid fa-star"></i> ${m.rating_percentage}%
                    </div>
                    <button style="position: absolute; top: 0.75rem; right: 0.75rem; background: rgba(10,12,20,0.8); border: none; width: 34px; height: 34px; border-radius: 50%; color: ${isFav ? 'var(--primary)' : '#fff'}; font-size: 1rem; cursor: pointer; backdrop-filter: blur(8px);" onclick="app.toggleWatchlist(${m.id}, event)">
                        <i class="fa-${isFav ? 'solid' : 'regular'} fa-heart"></i>
                    </button>
                </div>
                <div class="card-info">
                    <div class="card-title">${m.title}</div>
                    <div class="card-meta">
                        <span>${m.certificate} • ${m.language.split(',')[0]}</span>
                        <span style="color: var(--gold);">${m.genre.split(',')[0]}</span>
                    </div>
                    <button class="btn-book-quick">Book Tickets</button>
                </div>
            `;
            grid.appendChild(card);
        });
    },

    filterLanguage: function(lang, btn) {
        document.querySelectorAll(".filter-pills .filter-pill").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.state.activeLanguageFilter = lang;
        this.loadMovies().then(() => this.renderMovieGrid());
    },

    filterGenre: function(genre, btn) {
        document.querySelectorAll(".filter-pills .filter-pill").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.state.activeGenreFilter = genre;
        this.loadMovies().then(() => this.renderMovieGrid());
    },

    // ---------------- SEARCH ---------------- //

    handleSearchInput: async function(val) {
        const dropdown = document.getElementById("searchResultsDropdown");
        if (!val || val.trim().length === 0) {
            dropdown.classList.remove("active");
            return;
        }

        try {
            const res = await fetch(`/api/movies?search=${encodeURIComponent(val.trim())}`);
            const results = await res.json();

            dropdown.innerHTML = "";
            if (results.length === 0) {
                dropdown.innerHTML = `<div style="padding: 1rem; color: var(--text-muted); text-align: center;">No results found</div>`;
            } else {
                results.slice(0, 5).forEach(m => {
                    const item = document.createElement("div");
                    item.className = "search-item";
                    item.onclick = () => {
                        dropdown.classList.remove("active");
                        this.openMovieDetail(m.id);
                    };
                    item.innerHTML = `
                        <img src="${m.poster_url}" alt="${m.title}">
                        <div>
                            <div style="font-weight: 700; color: #fff;">${m.title}</div>
                            <div style="font-size: 0.8rem; color: var(--text-muted);">${m.language} • ${m.genre}</div>
                        </div>
                    `;
                    dropdown.appendChild(item);
                });
            }
            dropdown.classList.add("active");
        } catch (e) {
            console.error("Search failed", e);
        }
    },

    // ---------------- CITY PICKER ---------------- //

    openCityModal: function() {
        this.openModal("cityModal");
    },

    renderCityGrid: function() {
        const grid = document.getElementById("cityGrid");
        if (!grid) return;
        grid.innerHTML = "";

        this.state.cities.forEach(c => {
            const btn = document.createElement("button");
            btn.className = `city-picker-btn ${c.id === this.state.city.id ? 'active' : ''}`;
            btn.style.width = "100%";
            btn.style.justifyContent = "center";
            btn.innerHTML = `<i class="fa-solid fa-city"></i> ${c.name}`;
            btn.onclick = () => {
                this.state.city = { id: c.id, name: c.name };
                document.getElementById("selectedCityLabel").innerText = c.name;
                this.closeModal("cityModal");
                this.loadMovies().then(() => this.renderMovieGrid());
            };
            grid.appendChild(btn);
        });
    },

    // ---------------- MOVIE DETAIL MODAL & TRAILER ---------------- //

    openMovieDetail: async function(movieId) {
        try {
            const res = await fetch(`/api/movies/${movieId}`);
            const movie = await res.json();
            this.state.selectedMovie = movie;

            const container = document.getElementById("movieDetailContent");
            container.innerHTML = `
                <div class="movie-detail-banner" style="background-image: linear-gradient(90deg, rgba(10,12,20,0.95) 0%, rgba(10,12,20,0.7) 100%), url('${movie.poster_url}'); background-size: cover; background-position: center;">
                    <div style="position: relative; z-index: 2; display: flex; gap: 1.5rem; align-items: flex-end; width: 100%;">
                        <img src="${movie.poster_url}" style="width: 140px; height: 200px; object-fit: cover; border-radius: 14px; box-shadow: 0 10px 25px rgba(0,0,0,0.8); border: 2px solid var(--border-glass);">
                        <div style="flex: 1;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <h2 style="font-size: 2.2rem; font-weight: 800; line-height: 1.1; margin-bottom: 0.5rem;">${movie.title}</h2>
                                <button class="btn-secondary" style="background: rgba(239, 68, 68, 0.2); border-color: #ef4444; color: #ef4444; padding: 0.35rem 0.75rem; font-size: 0.8rem;" onclick="app.deleteMovie(${movie.id})">
                                    <i class="fa-solid fa-trash"></i> Delete
                                </button>
                            </div>
                            <div style="display: flex; gap: 1rem; color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.75rem;">
                                <span><i class="fa-solid fa-star" style="color: var(--gold);"></i> ${movie.rating_percentage}% (${(movie.rating_count/1000).toFixed(0)}K votes)</span>
                                <span><i class="fa-solid fa-clock"></i> ${movie.duration_mins}m</span>
                                <span>${movie.certificate}</span>
                            </div>
                            <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
                                ${movie.formats.map(f => `<span style="background: rgba(255,255,255,0.1); border: 1px solid var(--border-glass); padding: 0.25rem 0.6rem; border-radius: 8px; font-size: 0.75rem; font-weight: 600;">${f}</span>`).join('')}
                            </div>
                            <button class="btn-secondary" style="padding: 0.4rem 1rem; font-size: 0.85rem;" onclick="app.openTrailerModal('${movie.trailer_url}')">
                                <i class="fa-solid fa-play" style="color: var(--primary);"></i> Watch Trailer
                            </button>
                        </div>
                    </div>
                </div>

                <div class="detail-body">
                    <h4 style="color: var(--text-muted); margin-bottom: 0.5rem; font-size: 0.9rem; text-transform: uppercase;">About the movie</h4>
                    <p style="color: #cbd5e1; line-height: 1.6; margin-bottom: 1.5rem;">${movie.synopsis}</p>

                    <h4 style="color: var(--text-muted); margin-bottom: 0.5rem; font-size: 0.9rem; text-transform: uppercase;">Cast & Crew</h4>
                    <div class="cast-grid">
                        ${movie.cast.map(c => `
                            <div class="cast-card">
                                <img src="${c.avatar}" class="cast-avatar" alt="${c.name}">
                                <div style="font-weight: 700; font-size: 0.85rem;">${c.name}</div>
                                <div style="font-size: 0.75rem; color: var(--text-muted);">${c.role}</div>
                            </div>
                        `).join('')}
                    </div>

                    <div style="margin-top: 2rem; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: var(--text-muted); font-size: 0.85rem;">Language:</span>
                            <strong style="color: var(--gold);">${movie.language}</strong>
                        </div>
                        <button class="btn-primary" style="padding: 0.9rem 2rem; font-size: 1.1rem;" onclick="app.openShowtimesModal(${movie.id})">
                            Select Cinema & Showtimes <i class="fa-solid fa-arrow-right"></i>
                        </button>
                    </div>
                </div>
            `;

            this.openModal("movieDetailModal");
        } catch (e) {
            console.error("Failed to load movie detail", e);
        }
    },

    openTrailerModal: function(url) {
        const iframe = document.getElementById("trailerIframe");
        if (iframe) {
            iframe.src = url + "?autoplay=1";
        }
        this.openModal("trailerModal");
    },

    closeTrailerModal: function() {
        const iframe = document.getElementById("trailerIframe");
        if (iframe) iframe.src = "";
        this.closeModal("trailerModal");
    },

    // ---------------- SHOWTIMES & CINEMA MODAL ---------------- //

    openShowtimesModal: async function(movieId) {
        this.closeModal("movieDetailModal");
        const movie = this.state.selectedMovie;
        document.getElementById("stMovieTitle").innerText = movie.title;
        document.getElementById("stMovieMeta").innerText = `${movie.language} • ${movie.certificate} • ${movie.genre}`;

        const dateTabs = document.getElementById("dateTabs");
        dateTabs.innerHTML = "";

        const today = new Date();
        const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

        for (let i = 0; i < 4; i++) {
            const d = new Date(today);
            d.setDate(today.getDate() + i);

            const dateStr = d.toISOString().split('T')[0];
            if (i === 0) this.state.selectedDate = dateStr;

            const tab = document.createElement("div");
            tab.className = `date-tab ${i === 0 ? 'active' : ''}`;
            tab.innerHTML = `
                <div class="day">${i === 0 ? 'TODAY' : days[d.getDay()]}</div>
                <div class="date-num">${d.getDate()} ${months[d.getMonth()]}</div>
            `;
            tab.onclick = () => {
                document.querySelectorAll("#dateTabs .date-tab").forEach(t => t.classList.remove("active"));
                tab.classList.add("active");
                this.state.selectedDate = dateStr;
                this.loadShowtimes();
            };
            dateTabs.appendChild(tab);
        }

        await this.loadShowtimes();
        this.openModal("showtimesModal");
    },

    loadShowtimes: async function() {
        const cinemasList = document.getElementById("cinemasList");
        cinemasList.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted);"><i class="fa-solid fa-spinner fa-spin" style="font-size: 2rem;"></i> Loading showtimes...</div>`;

        try {
            const url = `/api/showtimes?movie_id=${this.state.selectedMovie.id}&city_id=${this.state.city.id}&date=${this.state.selectedDate}`;
            const res = await fetch(url);
            let cinemas = await res.json();

            if (cinemas.length === 0) {
                const fallbackUrl = `/api/showtimes?movie_id=${this.state.selectedMovie.id}&date=${this.state.selectedDate}`;
                const fbRes = await fetch(fallbackUrl);
                cinemas = await fbRes.json();
            }

            cinemasList.innerHTML = "";
            if (cinemas.length === 0) {
                cinemasList.innerHTML = `<div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                    <i class="fa-solid fa-calendar-xmark" style="font-size: 2.5rem; margin-bottom: 1rem; color: var(--primary);"></i>
                    <h4>No showtimes available for this date</h4>
                </div>`;
                return;
            }

            cinemas.forEach(c => {
                const card = document.createElement("div");
                card.className = "cinema-card";
                card.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <div class="cinema-title"><i class="fa-regular fa-heart" style="color: var(--primary);"></i> ${c.cinema_name}</div>
                            <div class="cinema-address">${c.cinema_address}</div>
                        </div>
                        <div style="display: flex; gap: 0.5rem;">
                            ${c.facilities.map(f => `<span style="font-size: 0.72rem; background: rgba(255,255,255,0.06); padding: 0.2rem 0.5rem; border-radius: 6px; color: var(--text-muted);">${f}</span>`).join('')}
                        </div>
                    </div>
                    <div class="showtime-btns" style="margin-top: 1rem;">
                        ${c.showtimes.map(st => `
                            <button class="showtime-btn" onclick="app.openSeatingModal(${st.showtime_id}, '${c.cinema_name}', '${st.time}', '${st.format}')">
                                <div class="time">${st.time}</div>
                                <div class="fmt">${st.format}</div>
                            </button>
                        `).join('')}
                    </div>
                `;
                cinemasList.appendChild(card);
            });
        } catch (e) {
            console.error("Failed to load showtimes", e);
        }
    },

    // ---------------- INTERACTIVE SEATING MATRIX ---------------- //

    openSeatingModal: async function(showtimeId, cinemaName, showTime, format) {
        this.closeModal("showtimesModal");
        this.state.selectedSeats = [];
        this.updateSeatCartUI();

        try {
            const res = await fetch(`/api/showtimes/${showtimeId}/seats`);
            const data = await res.json();
            this.state.selectedShowtime = { id: showtimeId, cinemaName, showTime, format, ...data.showtime };

            document.getElementById("seatScreenMovieTitle").innerText = this.state.selectedMovie.title;
            document.getElementById("seatScreenCinemaInfo").innerText = `${cinemaName} | ${this.state.selectedDate} ${showTime} (${format})`;

            const seatingArea = document.getElementById("seatingArea");
            seatingArea.innerHTML = "";

            const rowsMap = {};
            data.seats.forEach(s => {
                if (!rowsMap[s.row_label]) rowsMap[s.row_label] = [];
                rowsMap[s.row_label].push(s);
            });

            Object.keys(rowsMap).forEach(rowLabel => {
                const rowDiv = document.createElement("div");
                rowDiv.className = "seat-row";

                const labelDiv = document.createElement("div");
                labelDiv.className = "row-label";
                labelDiv.innerText = rowLabel;
                rowDiv.appendChild(labelDiv);

                rowsMap[rowLabel].forEach(s => {
                    const seatEl = document.createElement("div");
                    seatEl.className = `seat ${s.status === 'RESERVED' || s.status === 'BOOKED' ? 'reserved' : ''}`;
                    seatEl.innerText = s.seat_number;
                    seatEl.dataset.code = s.seat_code;
                    seatEl.dataset.tier = s.tier;
                    seatEl.dataset.price = s.price;

                    if (s.status === 'AVAILABLE') {
                        if (s.tier === 'Recliner') seatEl.style.borderColor = 'var(--gold)';
                        else if (s.tier === 'Prime') seatEl.style.borderColor = 'var(--cyan)';
                    }

                    if (s.status === 'AVAILABLE') {
                        seatEl.onclick = () => this.toggleSeatSelection(seatEl, s);
                    }
                    rowDiv.appendChild(seatEl);
                });

                seatingArea.appendChild(rowDiv);
            });

            this.openModal("seatingModal");
        } catch (e) {
            console.error("Failed to load seats", e);
        }
    },

    toggleSeatSelection: function(seatEl, seatObj) {
        const code = seatObj.seat_code;
        const index = this.state.selectedSeats.findIndex(s => s.seat_code === code);

        if (index > -1) {
            this.state.selectedSeats.splice(index, 1);
            seatEl.classList.remove("selected");
        } else {
            this.state.selectedSeats.push({
                seat_code: seatObj.seat_code,
                tier: seatObj.tier,
                price: seatObj.price
            });
            seatEl.classList.add("selected");
        }

        this.updateSeatCartUI();
    },

    updateSeatCartUI: function() {
        const label = document.getElementById("selectedSeatsLabel");
        const priceLabel = document.getElementById("totalSeatPriceLabel");

        if (this.state.selectedSeats.length === 0) {
            label.innerText = "None";
            priceLabel.innerText = "₹0";
            return;
        }

        const codes = this.state.selectedSeats.map(s => s.seat_code).join(", ");
        const total = this.state.selectedSeats.reduce((acc, s) => acc + s.price, 0);

        label.innerText = `${codes} (${this.state.selectedSeats.length} seats)`;
        priceLabel.innerText = `₹${total.toFixed(2)}`;
    },

    // ---------------- FOOD & BEVERAGE DRAWER ---------------- //

    proceedToFnB: function() {
        if (this.state.selectedSeats.length === 0) {
            alert("Please select at least 1 seat to proceed!");
            return;
        }
        this.closeModal("seatingModal");
        this.renderFnBGrid();
        this.openModal("fnbModal");
    },

    renderFnBGrid: function() {
        const grid = document.getElementById("fnbGrid");
        if (!grid) return;
        grid.innerHTML = "";

        this.state.fnbCatalog.forEach(item => {
            const qty = this.state.selectedFnB[item.id] || 0;
            const card = document.createElement("div");
            card.className = "fnb-card";

            card.innerHTML = `
                <img src="${item.image_url}" alt="${item.name}">
                <div style="flex: 1;">
                    <div style="font-weight: 700; font-size: 0.95rem;">${item.name}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.4rem;">${item.description}</div>
                    <div style="font-weight: 800; color: var(--gold);">₹${item.price.toFixed(2)}</div>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <button class="qty-btn" onclick="app.updateFnBQty(${item.id}, -1)">-</button>
                    <span style="font-weight: 700; font-size: 1rem; width: 16px; text-align: center;">${qty}</span>
                    <button class="qty-btn" onclick="app.updateFnBQty(${item.id}, 1)">+</button>
                </div>
            `;
            grid.appendChild(card);
        });
    },

    updateFnBQty: function(itemId, delta) {
        const current = this.state.selectedFnB[itemId] || 0;
        const next = Math.max(0, current + delta);
        if (next === 0) delete this.state.selectedFnB[itemId];
        else this.state.selectedFnB[itemId] = next;

        this.renderFnBGrid();
    },

    skipFnB: function() {
        this.state.selectedFnB = {};
        this.openPaymentModal();
    },

    // ---------------- CHECKOUT & PAYMENT ---------------- //

    openPaymentModal: function() {
        this.closeModal("fnbModal");
        this.state.appliedPromo = null;
        document.getElementById("promoInput").value = "";
        document.getElementById("promoMsg").innerText = "";
        document.getElementById("billDiscountRow").style.display = "none";

        if (this.state.currentUser) {
            document.getElementById("payUserName").value = this.state.currentUser.name;
            document.getElementById("payUserEmail").value = this.state.currentUser.email;
        }

        this.calculateBill();
        this.openModal("paymentModal");
    },

    calculateBill: function() {
        const seatTotal = this.state.selectedSeats.reduce((acc, s) => acc + s.price, 0);

        let fnbTotal = 0;
        Object.keys(this.state.selectedFnB).forEach(id => {
            const item = this.state.fnbCatalog.find(f => f.id == id);
            if (item) fnbTotal += item.price * this.state.selectedFnB[id];
        });

        const subtotal = seatTotal + fnbTotal;
        const convFee = (35.0 * this.state.selectedSeats.length) * 1.18;

        let discount = 0;
        if (this.state.appliedPromo) {
            discount = this.state.appliedPromo.discount_amount;
        }

        const grandTotal = Math.max(0, subtotal + convFee - discount);

        document.getElementById("billTicketsSubtotal").innerText = `₹${seatTotal.toFixed(2)}`;
        document.getElementById("billFnBSubtotal").innerText = `₹${fnbTotal.toFixed(2)}`;
        document.getElementById("billConvenienceFee").innerText = `₹${convFee.toFixed(2)}`;
        document.getElementById("billTotalPayable").innerText = `₹${grandTotal.toFixed(2)}`;
    },

    applyPromo: async function() {
        const code = document.getElementById("promoInput").value.trim();
        const msgDiv = document.getElementById("promoMsg");
        if (!code) return;

        const seatTotal = this.state.selectedSeats.reduce((acc, s) => acc + s.price, 0);

        try {
            const res = await fetch("/api/promos/validate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ code: code, amount: seatTotal })
            });

            const data = await res.json();
            if (res.ok && data.valid) {
                this.state.appliedPromo = data;
                msgDiv.style.color = "#4ade80";
                msgDiv.innerText = data.message;

                document.getElementById("billDiscountRow").style.display = "flex";
                document.getElementById("billDiscountAmount").innerText = `-₹${data.discount_amount.toFixed(2)}`;
                this.calculateBill();
            } else {
                msgDiv.style.color = "#ef4444";
                msgDiv.innerText = data.detail || "Invalid promo code";
            }
        } catch (e) {
            msgDiv.style.color = "#ef4444";
            msgDiv.innerText = "Failed to validate promo";
        }
    },

    processPayment: async function() {
        const name = document.getElementById("payUserName").value.trim();
        const email = document.getElementById("payUserEmail").value.trim();

        if (!name || !email) {
            alert("Please provide your name and email!");
            return;
        }

        this.state.userEmail = email;

        const fnbList = [];
        Object.keys(this.state.selectedFnB).forEach(id => {
            const item = this.state.fnbCatalog.find(f => f.id == id);
            if (item) {
                fnbList.push({
                    id: item.id,
                    name: item.name,
                    qty: this.state.selectedFnB[id],
                    price: item.price
                });
            }
        });

        const payload = {
            showtime_id: this.state.selectedShowtime.id,
            user_name: name,
            user_email: email,
            user_phone: "9876543210",
            seats: this.state.selectedSeats,
            fnb: fnbList,
            promo_code: this.state.appliedPromo ? this.state.appliedPromo.code : null,
            payment_method: "UPI"
        };

        try {
            const res = await fetch("/api/bookings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (res.ok && data.success) {
                this.closeModal("paymentModal");
                this.renderETicket(data);
                this.openModal("ticketModal");
            } else {
                alert(data.detail || "Booking failed!");
            }
        } catch (e) {
            console.error("Booking failed", e);
            alert("Network error processing payment");
        }
    },

    // ---------------- DIGITAL E-TICKET RENDERING ---------------- //

    renderETicket: function(ticketData) {
        const container = document.getElementById("eTicketContent");
        const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(ticketData.qr_payload)}`;

        container.innerHTML = `
            <div class="e-ticket">
                <div class="ticket-header">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <div style="width: 32px; height: 32px; background: var(--primary); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 800;">ST</div>
                        <span style="font-weight: 900; font-size: 1.2rem; background: linear-gradient(90deg, #fff, var(--gold)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">ShowTime E-Ticket</span>
                    </div>
                    <span style="background: rgba(74, 222, 128, 0.2); color: #4ade80; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem; font-weight: 700;">CONFIRMED</span>
                </div>

                <div style="display: flex; gap: 1.25rem; margin-bottom: 1.5rem;">
                    <img src="${ticketData.poster_url}" style="width: 90px; height: 130px; object-fit: cover; border-radius: 12px;">
                    <div>
                        <h3 style="font-size: 1.3rem; font-weight: 800; margin-bottom: 0.3rem;">${ticketData.movie_title}</h3>
                        <p style="color: var(--gold); font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem;">${ticketData.format} | ${ticketData.cinema_name}</p>
                        <p style="color: var(--text-muted); font-size: 0.8rem; margin-bottom: 0.5rem;">${ticketData.cinema_address}</p>
                        <div style="display: flex; gap: 1rem; font-size: 0.85rem; font-weight: 700;">
                            <span><i class="fa-regular fa-calendar" style="color: var(--primary);"></i> ${ticketData.date}</span>
                            <span><i class="fa-regular fa-clock" style="color: var(--primary);"></i> ${ticketData.time}</span>
                        </div>
                    </div>
                </div>

                <div style="background: rgba(0,0,0,0.3); border: 1px solid var(--border-glass); border-radius: 16px; padding: 1.25rem; display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                    <div>
                        <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">BOOKING ID</div>
                        <div style="font-weight: 800; font-size: 1.1rem; color: var(--cyan); letter-spacing: 1px;">${ticketData.booking_id}</div>
                        <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.5rem; text-transform: uppercase;">SEATS (${ticketData.seats.length})</div>
                        <div style="font-weight: 800; font-size: 1.2rem; color: var(--primary);">${ticketData.seats.join(", ")}</div>
                    </div>
                    <div class="qr-placeholder">
                        <img src="${qrUrl}" alt="Ticket QR">
                    </div>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 0.8rem; color: var(--text-muted);">Total Paid:</div>
                        <div style="font-size: 1.2rem; font-weight: 800; color: #fff;">₹${ticketData.total_amount.toFixed(2)}</div>
                    </div>
                    <button class="btn-primary" onclick="window.print()">
                        <i class="fa-solid fa-print"></i> Print / Save Ticket
                    </button>
                </div>
            </div>
        `;
    },

    // ---------------- MY BOOKINGS ---------------- //

    openMyBookingsModal: function() {
        document.getElementById("myBookingsEmailInput").value = this.state.userEmail;
        this.fetchMyBookings();
        this.openModal("myBookingsModal");
    },

    fetchMyBookings: async function() {
        const email = document.getElementById("myBookingsEmailInput").value.trim();
        const listDiv = document.getElementById("myBookingsList");
        if (!email) return;

        listDiv.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted);"><i class="fa-solid fa-spinner fa-spin"></i> Fetching tickets...</div>`;

        try {
            const res = await fetch(`/api/my-bookings?email=${encodeURIComponent(email)}`);
            const bookings = await res.json();

            listDiv.innerHTML = "";
            if (bookings.length === 0) {
                listDiv.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted);">No bookings found for this email.</div>`;
                return;
            }

            bookings.forEach(b => {
                const card = document.createElement("div");
                card.className = "cinema-card";
                card.style.display = "flex";
                card.style.gap = "1rem";
                card.style.alignItems = "center";

                const seatCodes = b.seats.map(s => s.seat_code).join(", ");

                card.innerHTML = `
                    <img src="${b.poster_url}" style="width: 60px; height: 85px; object-fit: cover; border-radius: 8px;">
                    <div style="flex: 1;">
                        <div style="font-weight: 800; font-size: 1.1rem; color: #fff;">${b.movie_title}</div>
                        <div style="font-size: 0.82rem; color: var(--gold);">${b.cinema_name} • ${b.format}</div>
                        <div style="font-size: 0.8rem; color: var(--text-muted);">${b.date} at ${b.time} | Seats: <strong style="color: var(--primary);">${seatCodes}</strong></div>
                    </div>
                    <button class="btn-secondary" style="padding: 0.5rem 1rem; font-size: 0.85rem;" onclick="app.viewPastBooking('${b.booking_id}')">
                        View Ticket
                    </button>
                `;
                listDiv.appendChild(card);
            });
        } catch (e) {
            console.error("Failed to fetch my bookings", e);
        }
    },

    viewPastBooking: async function(bookingId) {
        try {
            const res = await fetch(`/api/bookings/${bookingId}`);
            const data = await res.json();
            this.closeModal("myBookingsModal");
            this.renderETicket({
                ...data,
                seats: data.seats.map(s => s.seat_code)
            });
            this.openModal("ticketModal");
        } catch (e) {
            console.error("Failed to view past booking", e);
        }
    },

    // ---------------- MODALS UTILITY ---------------- //

    openModal: function(id) {
        const modal = document.getElementById(id);
        if (modal) modal.classList.add("active");
    },

    closeModal: function(id) {
        const modal = document.getElementById(id);
        if (modal) modal.classList.remove("active");
    },

    resetHome: function() {
        window.location.reload();
    }
};

document.addEventListener("DOMContentLoaded", () => {
    app.init();
});
