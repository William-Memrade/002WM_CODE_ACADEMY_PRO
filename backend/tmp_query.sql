SELECT polname, polcmd, pg_get_expr(polqual, polrelid) AS using_expr, pg_get_expr(polwithcheck, polrelid) AS with_check FROM pg_policy WHERE polrelid = 'users'::regclass;
