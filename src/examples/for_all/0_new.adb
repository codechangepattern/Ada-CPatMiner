function Is_In (V : Version; VS : Version_Set) return Boolean is
begin
    return (for all R of VS => Satisfies (V, R));
end Is_In;