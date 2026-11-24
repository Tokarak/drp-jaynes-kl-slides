# DRP session build. `make` = figures + final animations + slides.
PY      := .venv/bin/python
MANIM   := .venv/bin/manim
SCENES  := BayesUpdate LikelihoodConcentration
MEDIA   := build/media

.PHONY: all figures anim anim-draft slides preview pdf standalone clean

all: figures anim slides

figures:
	$(PY) figures/make_figures.py slides/fig

anim-draft:          ## fast 480p15 render while iterating
	cd anim && ../$(MANIM) -ql --media_dir ../$(MEDIA) kl_scenes.py $(SCENES)
	mkdir -p slides/media && cp $(MEDIA)/videos/kl_scenes/480p15/*.mp4 slides/media/

anim:                ## final 1080p60
	cd anim && ../$(MANIM) -qh --media_dir ../$(MEDIA) kl_scenes.py $(SCENES)
	mkdir -p slides/media && cp $(MEDIA)/videos/kl_scenes/1080p60/*.mp4 slides/media/

slides:
	cd slides && quarto render index.qmd

preview:
	cd slides && quarto preview index.qmd

pdf:                 ## static handout (needs Chrome); videos/widgets become still frames
	cd slides && quarto render index.qmd --to pdf 2>/dev/null || echo "use ?print-pdf in the browser"

standalone:          ## one HTML file that runs from disk (send by WhatsApp etc.)
	cd slides && quarto render index.qmd -M embed-resources:true --output standalone_raw.html
	mkdir -p build && $(PY) tools/make_standalone.py slides/standalone_raw.html build/expected-evidence.html
	rm -f slides/standalone_raw.html

clean:
	rm -rf build slides/_site slides/index_files slides/index.html slides/.quarto
