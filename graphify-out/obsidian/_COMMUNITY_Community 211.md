---
type: community
cohesion: 0.20
members: 10
---

# Community 211

**Cohesion:** 0.20 - loosely connected
**Members:** 10 nodes

## Members
- [[dot-test_admin_can_update_any_profile()]] - code - Academia/Academy_Test/backend/tests/test_rls.py
- [[dot-test_student_can_update_own_profile()]] - code - Academia/Academy_Test/backend/tests/test_rls.py
- [[dot-test_student_cannot_delete_users()]] - code - Academia/Academy_Test/backend/tests/test_rls.py
- [[dot-test_student_cannot_update_other_profile()]] - code - Academia/Academy_Test/backend/tests/test_rls.py
- [[Admin can update any user's profile.]] - rationale - Academia/Academy_Test/backend/tests/test_rls.py
- [[Student can update their own bio.]] - rationale - Academia/Academy_Test/backend/tests/test_rls.py
- [[Student cannot update another user's profile.]] - rationale - Academia/Academy_Test/backend/tests/test_rls.py
- [[Students cannot delete users.]] - rationale - Academia/Academy_Test/backend/tests/test_rls.py
- [[TestUserRLS]] - code - Academia/Academy_Test/backend/tests/test_rls.py
- [[Verify users can only modify their own records.]] - rationale - Academia/Academy_Test/backend/tests/test_rls.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_211
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Community 146]]
- 4 edges to [[_COMMUNITY_Community 198]]
- 1 edge to [[_COMMUNITY_Community 115]]

## Top bridge nodes
- [[dot-test_admin_can_update_any_profile()]] - degree 4, connects to 2 communities
- [[dot-test_student_can_update_own_profile()]] - degree 4, connects to 2 communities
- [[dot-test_student_cannot_delete_users()]] - degree 4, connects to 2 communities
- [[dot-test_student_cannot_update_other_profile()]] - degree 4, connects to 2 communities
- [[TestUserRLS]] - degree 6, connects to 1 community