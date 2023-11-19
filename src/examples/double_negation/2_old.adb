function Test_2 (A : Integer; B : Integer) return Boolean is
    C : constant Boolean := not (not (A < B));
begin
    return C;
end Test_2;