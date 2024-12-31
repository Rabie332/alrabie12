.SILENT: update branch lint git-clean
.PHONY: update branch lint git-clean

BRANCH=14.0

.DEFAULT: help
help:
	@echo "make update --> sync with upstream repo"
	@echo "make branch n=branch_name --> Create and switch to branch :branch_name"
	@echo "make lint --> Check odoo code style"
	@echo "make git-clean -->Clean Up Local Git Branches"

update:
	git checkout $(BRANCH)
	git fetch origin $(BRANCH)
	git merge origin/$(BRANCH)

branch:
	git checkout $(BRANCH)
	git fetch origin $(BRANCH)
	git merge origin/$(BRANCH)
	git checkout -b $(BRANCH)-$(n)

lint:
	docker run --pull always -it --rm --volume $$(pwd):/code registry.hadooc.com/devops/ci:lint14

git-clean:
	git branch --list '$(BRANCH)-*' | xargs -r git branch -D
