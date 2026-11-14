# Third-party notices

The `pyJianYingDraft` directory is copied from `scripts/vendor/pyJianYingDraft` in [luoluoluo22/jianying-editor-skill](https://github.com/luoluoluo22/jianying-editor-skill), commit `32c56928ded4f9e2c2b80e099dc7abb793d2c30b`.

The enclosing skill project is copyright (c) 2026 luoluoluo22, MIT licensed. Its license is included in `JIAN YING SKILL LICENSE.txt`.

The underlying library is derived from [GuanYixuan/pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft), copyright GuanYixuan (管奕轩), licensed under Apache License 2.0. The upstream license is included in `PYJIANYINGDRAFT_LICENSE.txt`.

Local modification: the optional Windows UI automation import and associated deprecated aliases are guarded when `uiautomation` is unavailable. Core draft generation is unchanged. This workflow does not invoke the UI automation controller.
