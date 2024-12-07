% Regras Prolog para verificar compatibilidade de doação de sangue
pode_doar_sangue(Idade, Peso, TipoDoador, RhDoador, TipoReceptor, RhReceptor) :-
    Idade >= 18, Idade =< 65,
    Peso > 50,
    compatibilidade_sanguinea(TipoDoador, TipoReceptor),
    compatibilidade_rh(RhDoador, RhReceptor).

compatibilidade_sanguinea(o, _).
compatibilidade_sanguinea(a, a).
compatibilidade_sanguinea(a, ab).
compatibilidade_sanguinea(b, b).
compatibilidade_sanguinea(b, ab).
compatibilidade_sanguinea(ab, ab).

compatibilidade_rh(negativo, negativo).
compatibilidade_rh(negativo, positivo).
compatibilidade_rh(positivo, positivo).
