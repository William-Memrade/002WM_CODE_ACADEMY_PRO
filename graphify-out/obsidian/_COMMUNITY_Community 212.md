---
type: community
cohesion: 0.20
members: 10
---

# Community 212

**Cohesion:** 0.20 - loosely connected
**Members:** 10 nodes

## Members
- [[dot-test_teacher_can_update_own_course()]] - code - Academia/Academy_Test/backend/tests/test_rls.py
- [[dot-test_teacher_cannot_create_courses()]] - code - Academia/Academy_Test/backend/tests/test_rls.py
- [[dot-test_teacher_cannot_see_other_teacher_courses()]] - code - Academia/Academy_Test/backend/tests/test_rls.py
- [[dot-test_teacher_sees_own_courses()]] - code - Academia/Academy_Test/backend/tests/test_rls.py
- [[Teacher can see their assigned course (active or not).]] - rationale - Academia/Academy_Test/backend/tests/test_rls.py
- [[Teacher can update their own course.]] - rationale - Academia/Academy_Test/backend/tests/test_rls.py
- [[Teacher cannot see inactive courses from another teacher.]] - rationale - Academia/Academy_Test/backend/tests/test_rls.py
- [[Teachers cannot INSERT courses (admin only).]] - rationale - Academia/Academy_Test/backend/tests/test_rls.py
- [[TestTeacherRLS]] - code - Academia/Academy_Test/backend/tests/test_rls.py
- [[Verify teachers can only seeedit their own courses.]] - rationale - Academia/Academy_Test/backend/tests/test_rls.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_212
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Community 146]]
- 4 edges to [[_COMMUNITY_Community 198]]
- 1 edge to [[_COMMUNITY_Community 115]]

## Top bridge nodes
- [[dot-test_teacher_can_update_own_course()]] - degree 4, connects to 2 communities
- [[dot-test_teacher_cannot_create_courses()]] - degree 4, connects to 2 communities
- [[dot-test_teacher_cannot_see_other_teacher_courses()]] - degree 4, connects to 2 communities
- [[dot-test_teacher_sees_own_courses()]] - degree 4, connects to 2 communities
- [[TestTeacherRLS]] - degree 6, connects to 1 community