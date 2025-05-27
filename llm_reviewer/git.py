import gitlab
from gitlab.exceptions import GitlabAuthenticationError
import os
from typing import Any, Dict

git_base_url = os.environ["GIT_BASE_URL"]


class Git:
    def __init__(self, token: str, url=git_base_url):
        self.gl = gitlab.Gitlab(url=url, private_token=token)

    def auth(self):
        try:
            self.gl.auth()
        except GitlabAuthenticationError as e:
            raise RuntimeError(
                "Falha na autenticação: verifique se o token é válido "
                "e se tem scope `api` ou `read_api`"
            ) from e

    def get_diff(self, project_id: int | str, merge_request_iid: int):
        self.auth()
        project_obj = self.gl.projects.get(project_id)
        mr_obj = project_obj.mergerequests.get(merge_request_iid)
        diffs = mr_obj.changes()
        all_diffs = []
        for change in diffs["changes"]:
            file_info = (
                f"File: {change.get('new_path', change.get('old_path', 'unknown'))}\n"
            )
            all_diffs.append(file_info + change["diff"])
        return "\n\n".join(all_diffs)

    def write_comment(
        self, project_id: int | str, merge_request_iid: int | str, comment: str
    ):
        self.auth()
        project_obj = self.gl.projects.get(project_id)
        mr_obj = project_obj.mergerequests.get(merge_request_iid)
        discussion_id = None
        discussions = mr_obj.discussions.list()

        for discussion in discussions:
            discussion_notes = discussion.attributes.get("notes")
            if discussion_notes is not None:
                for note in discussion_notes:
                    if note.get("body").find("Code Review Documentation") != -1:
                        discussion_id = note.get("id")

        if discussion_id is None:
            mr_obj.notes.create({"body": comment})
            return

        mr_obj.notes.update(id=discussion_id, new_data={"body": comment})
