function Is_In (V : Version; VS : Version_Set) return Boolean is
begin
    for R of VS loop
        if not Satisfies (V, R) then
            return False;
        end if;
    end loop;

    return True;
end Is_In;