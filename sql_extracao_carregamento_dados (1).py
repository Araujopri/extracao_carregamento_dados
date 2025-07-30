'''

    Este trecho de código SQL cria uma tabela temporária chamada "qtd_avaliacoes_curso".
    A tabela resultante contém três colunas: "course", "qtd" e "ultima_atv".
    A coluna "course" armazena o nome do curso.
    A coluna "qtd" armazena a quantidade de avaliações para cada curso.
    A coluna "ultima_atv" armazena o ID da última avaliação para cada curso.
    A tabela temporária é criada a partir da tabela "mdl_quiz".
    A cláusula WHERE filtra os registros da tabela "mdl_quiz" onde o nome começa com "Avaliação".
    A cláusula GROUP BY agrupa os registros por curso.
'''
consulta_ceadex = '''
with qtd_avaliacoes_curso as (
   select course, count(*) as qtd, max(id) as ultima_atv
   from mdl_quiz
   where mdl_quiz.name like 'Avaliação%'
   group by course
)
-- Esta seleção retorna informações sobre os inscritos em um curso.
-- Os campos selecionados incluem o posto ou graduação do inscrito, seu nome, identidade, CPF, e-mail, arma ou quadro de serviço,
-- sexo, data de inscrição no curso, mês da inscrição, data de encerramento (se houver), nome do curso, organização militar,
-- região militar, código CGCFEx e uma lista concatenada de avaliações, notas finais e total de tentativas para cada avaliação.
select
	distinct on
	(nome_inscrito)
         nome_guerra as "posto_graduacao",
	nome_usuario as "nome_inscrito",
	identidade,
	cpf,
	qms as "arma_quadro_servico",
	sexo,
	data_inscricao_curso,
	extract(month
from
	data_inscricao_curso::date) as mes_inscricao,
	case
		when extract(year
	from
		termino_ultima_tentativa::date) = 1969 then null
		else TO_CHAR(termino_ultima_tentativa::date,
		'DD-MM-YYYY'::text)
	end as "data_encerramento",
	sala as "nome_curso",
	om,
	rm,
	cgcfex,
	STRING_AGG(avaliacao || ' =  ' || coalesce(nota_final,
	maior_nota,
	0)|| ' -  Tentativas: ' || coalesce(total_tentativas,
	0),
	'  /  '
order by
	avaliacao) as nota_avaliacao,
	-- Esta seleção de código é responsável por determinar o status e o mês de encerramento de um curso com base em várias condições.
	-- A primeira parte do código utiliza a função DATE_PART para calcular a diferença em dias entre a data atual e a data de inscrição do curso.
	-- Em seguida, são verificadas as seguintes condições:
	-- - Se a diferença for menor ou igual a 90 dias e a última tentativa da última atividade for nula ou a maior nota da última atividade for menor que 5.0, o status é definido como 'Em andamento'.
	-- - Se a diferença for maior que 90 dias, a nota final for menor que 5.0 e a maior nota da última atividade for menor que 5.0, o status é definido como 'Abandono'.
	-- - Se a última tentativa da última atividade for maior ou igual ao número máximo de tentativas e a maior nota da última atividade for menor que a nota para passar, o status é definido como 'Reprovado'.
	-- - Se a maior nota da última atividade for maior ou igual à nota para passar e todas as avaliações forem feitas, o status é definido como 'Aprovado'.
	-- Caso nenhuma das condições seja atendida, o status é definido como vazio.
	-- A segunda parte do código verifica se o curso está em andamento ou abandonado.
	-- Se a primeira parte das condições for atendida, ou seja, se a diferença for menor ou igual a 90 dias e a última tentativa da última atividade for nula ou a maior nota da última atividade for menor que 5.0,
	-- então o mês de encerramento é definido como NULL.
	-- Caso contrário, o mês de encerramento é definido como o mês de término da última tentativa convertido para o formato 'TMMonth'.
	-- O resultado final é uma tabela com as colunas 'status' e 'mes_encerramento', que indicam o status do curso e o mês de encerramento, respectivamente.
         case
		when DATE_PART('day',
		current_date::timestamp - data_inscricao_curso::timestamp) <= 90
		and (ultima_tentativa_ultima_atv is null
			or (ultima_tentativa_ultima_atv = 1
				and coalesce(maior_nota_ultima_atv,
				0) < 5.0)
				or (ultima_tentativa_ultima_atv = 2
					and coalesce(maior_nota_ultima_atv,
					0) < 5.0)
                         ) then 'Em andamento'
		when DATE_PART('day',
		current_date::timestamp - data_inscricao_curso::timestamp) > 90
		and coalesce(nota_final,
		0) < 5.0
		and coalesce(maior_nota_ultima_atv,
		0) < 5.0 then 'Abandono'
		when ultima_tentativa_ultima_atv >= max_de_tentativas
		and coalesce(maior_nota_ultima_atv,
		0) < nota_para_passar then 'Reprovado'
		when coalesce(maior_nota_ultima_atv,
		0) >= nota_para_passar
		and avaliacoes_feitas = qtd_avaliacoes then 'Aprovado'
		else ''
	end as status,
	case
		when (DATE_PART('day',
		current_date::timestamp - data_inscricao_curso::timestamp) <= 90
			and (ultima_tentativa_ultima_atv is null
				or (ultima_tentativa_ultima_atv = 1
					and coalesce(maior_nota_ultima_atv,
					0) < 5.0)
					or (ultima_tentativa_ultima_atv = 2
						and coalesce(maior_nota_ultima_atv,
						0) < 5.0)
                         )
                )
		or (DATE_PART('day',
		current_date::timestamp - data_inscricao_curso::timestamp) > 90
			and coalesce(nota_final,
			0) < 5.0
				and coalesce(maior_nota_ultima_atv,
				0) < 5.0
                ) then null
		else TO_CHAR(termino_ultima_tentativa::date,
		'TMMonth')
	end as mes_encerramento
/*
Esta seleção de consulta retorna informações detalhadas sobre os alunos matriculados em um curso específico, juntamente com os dados relacionados às avaliações realizadas por esses alunos.

Os campos retornados incluem:
- curso: o nome do curso em que o aluno está matriculado
- sala: a sala em que o aluno está alocado
- identidade: o número de identidade do aluno
- nome_guerra: o nome de guerra do aluno
- nome_usuario: o nome completo do aluno
- email: o endereço de e-mail do aluno
- om: organizacao militar
- codom: a data de registro do código da organização militar do aluno
- sexo: o sexo do aluno (Masculino ou Feminino)
- cpf: o número do CPF do aluno
- qms: a arma ou quadro de serviço do aluno
- rm: o número do RM 
- cgcfex: o número do CGCFEx  do aluno
- avaliacao: o nome da avaliação
- max_de_tentativas: o número máximo de tentativas permitidas para a avaliação
- nota_para_passar: a nota mínima necessária para passar na avaliação (padrão: 5)
- nota_final: a nota final obtida pelo aluno na avaliação
- data_inscricao_curso: a data de inscrição do aluno no curso
- ultima_tentativa: o número da última tentativa feita pelo aluno na avaliação
- maior_nota: a maior nota obtida pelo aluno em todas as avaliações do mesmo tipo
- termino_ultima_tentativa: a data e hora de término da última tentativa feita pelo aluno na avaliação
- avaliacoes_feitas: o número total de avaliações feitas pelo aluno no curso
- total_tentativas: o número total de tentativas concluídas pelo aluno na avaliação
- ultima_tentativa_ultima_atv: o número de tentativas feitas pelo aluno na última avaliação do mesmo tipo
- maior_nota_ultima_atv: a maior nota obtida pelo aluno na última avaliação do mesmo tipo
- qtd_avaliacoes: o número total de avaliações disponíveis no curso
- idquiz: o ID da avaliação
- id_user: o ID do usuário/aluno

A seleção é baseada em várias junções (INNER JOIN e LEFT JOIN) entre as tabelas do banco de dados, como alunos_matriculados_curso, mdl_quiz, mdl_grade_items, qtd_avaliacoes_curso, mdl_grade_grades, mdl_user, mdl_user_info_data, mdl_user_lastaccess e mdl_quiz_attempts.

A cláusula WHERE filtra os resultados para um curso específico, que é passado como parâmetro (%%COURSEID%%).

Os resultados são retornados na tabela "dados".
*/
from
	(
	select
		distinct
                            matriculado.curso,
		matriculado.sala,
		matriculado.identidade,
		matriculado.nome_guerra,
		matriculado.nome as nome_usuario,
		om.data as om,
		codom.data as codom,
		case
			when sexo.data = '1' then 'Masculino'
			when sexo.data = '2' then 'Feminino'
		end as sexo,
		cpf.data as cpf,
		qms.data as qms,
		mdl_ceadex_om_cgfex.rm,
		mdl_ceadex_om_cgfex.cgcfex,
		mdl_quiz.name as avaliacao,
		mdl_quiz.attempts as max_de_tentativas,
		case
			when coalesce(mdl_grade_items.gradepass,
			0) = 0 then 5
			else mdl_grade_items.gradepass
		end as nota_para_passar,
		ROUND(mdl_grade_grades.finalgrade,
		2) as nota_final,
		matriculado.data_inscricao_curso,
		(
		select
			attempt
		from
			mdl_quiz_attempts
		where
			mdl_quiz_attempts.quiz = mdl_quiz.id
			and mdl_quiz_attempts.userid = matriculado.id_user
		order by
			mdl_quiz.name desc
		limit 1) as ultima_tentativa,
		(
		select
			grade
		from
			mdl_quiz_grades
		where
			mdl_quiz_grades.quiz = mdl_quiz.id
			and mdl_quiz_grades.userid = matriculado.id_user
			and mdl_quiz.name like 'Avalia%'
		order by
			coalesce(grade,
			0) desc
		limit 1) as maior_nota,
		(
		select
			BIGINT_TO_DATETIME(timefinish)
		from
			mdl_quiz
		inner join mdl_quiz_attempts
                                    on
			(mdl_quiz.id = mdl_quiz_attempts.quiz)
		where
			mdl_quiz.course = matriculado.id_course
			and mdl_quiz_attempts.userid = matriculado.id_user
			and mdl_quiz.name like 'Avalia%'
		order by
			mdl_quiz.name desc
		limit 1) as termino_ultima_tentativa,
		(
		select
			COUNT(distinct mdl_quiz.id)
		from
			mdl_quiz
		inner join mdl_quiz_attempts
                                    on
			(mdl_quiz.id = mdl_quiz_attempts.quiz)
		where
			mdl_quiz.course = matriculado.id_course
			and mdl_quiz_attempts.userid = matriculado.id_user
			and mdl_quiz.name like 'Avaliação%') as avaliacoes_feitas,
		(
		select
			COUNT(attempt)
		from
			mdl_quiz_attempts
		where
			mdl_quiz_attempts.quiz = mdl_quiz.id
			and mdl_quiz_attempts.userid = matriculado.id_user
			and state = 'finished'
			and mdl_quiz.name like 'Avalia%'
                            ) as total_tentativas,
		(
		select
			tentativas
		from
			(
			select
				mdl_quiz_attempts.quiz as quiz,
				COUNT(mdl_quiz_attempts.attempt) as tentativas
			from
				mdl_quiz
			inner join mdl_quiz_attempts
                                                on
				(mdl_quiz.id = mdl_quiz_attempts.quiz)
			where
				mdl_quiz.course = matriculado.id_course
				and mdl_quiz_attempts.userid = matriculado.id_user
				and state = 'finished'
				and mdl_quiz.name like 'Avalia%'
			group by
				1
			order by
				1 desc
			limit 1
                                ) x
                            ) as ultima_tentativa_ultima_atv,
		(
		select
			mdl_quiz_grades.grade
		from
			mdl_quiz
		inner join mdl_quiz_grades
                                    on
			(mdl_quiz.id = mdl_quiz_grades.quiz)
		where
			mdl_quiz.course = matriculado.id_course
			and mdl_quiz_grades.userid = matriculado.id_user
			and mdl_quiz.name like 'Avalia%'
		order by
			mdl_quiz.name desc
		limit 1
                            ) as maior_nota_ultima_atv,
		qtd_avaliacoes_curso.qtd as qtd_avaliacoes,
		mdl_quiz.id as idquiz,
		matriculado.id_user
	from
		ceadex.alunos_matriculados_curso matriculado
	inner join mdl_quiz as mdl_quiz
                    on
		(mdl_quiz.course = matriculado.id_course
			and mdl_quiz.name like 'Avaliação%')
	inner join mdl_grade_items as mdl_grade_items
                    on
		matriculado.id_course = mdl_grade_items.courseid
		and
                            mdl_grade_items.iteminstance = mdl_quiz.id
	inner join qtd_avaliacoes_curso
                    on
		(qtd_avaliacoes_curso.course = matriculado.id_course)
	left join mdl_grade_grades
                    on
		mdl_grade_items.id = mdl_grade_grades.itemid
			and
                            mdl_grade_grades.userid = matriculado.id_user
		left join mdl_user as usuario
                    on
			(usuario.id = matriculado.id_user)
		left join mdl_user_info_data as om
                    on
			(om.userid = matriculado.id_user
				and om.fieldid = 7)
		left join mdl_user_info_data as codom
                    on
			(codom.userid = matriculado.id_user
				and codom.fieldid = 6)
		left join mdl_user_info_data as sexo
                    on
			(sexo.userid = matriculado.id_user
				and sexo.fieldid = 8)
		left join mdl_user_info_data as cpf
                    on
			(cpf.userid = matriculado.id_user
				and cpf.fieldid = 10)
		left join mdl_user_info_data as qms
                    on
			(qms.userid = matriculado.id_user
				and qms.fieldid = 11)
		left join ceadex.mdl_ceadex_om_cgfex
                    on
			(mdl_ceadex_om_cgfex.codom = codom.data)
		left join mdl_user_lastaccess as mdl_user_lastaccess
                    on
			(mdl_user_lastaccess.userid = matriculado.id_user
				and
                                mdl_user_lastaccess.courseid = matriculado.id_course)
		where
			matriculado.id_course  in (11157,
											11138,
											11145,
											11130,
											11137,
											11132,
											11129,
											11128,
											11152,
											11153,
											11136,
											11140,
											11134,
											11135,
											11144,
											11150,
											11141,
											11131,
											11139,
											11133,
											11156,
											11160,
											11159,
											12009,
											11455) 
) dados
/*
Este trecho de código SQL realiza uma seleção de dados e aplica uma série de operações para agrupar e ordenar os resultados.

A cláusula GROUP BY é utilizada para agrupar os resultados com base nas colunas especificadas: qtd_avaliacoes, avaliacoes_feitas, nota_para_passar, max_de_tentativas, maior_nota_ultima_atv, ultima_tentativa_ultima_atv, sala, identidade, nome_guerra, nome_usuario, email, om, codom, sexo, cpf, qms, rm, cgcfex, data_inscricao_curso, termino_ultima_tentativa, total_tentativas, nota_final e 16.

A cláusula ORDER BY é utilizada para ordenar os resultados em ordem crescente com base na coluna nome_inscrito.

Este trecho de código é parte de uma query mais extensa e seu propósito específico depende do contexto em que é utilizado.
*/
group by
	qtd_avaliacoes,
	avaliacoes_feitas,
	nota_para_passar,
	max_de_tentativas,
	maior_nota_ultima_atv,
	ultima_tentativa_ultima_atv,
	sala,
	identidade,
	nome_guerra,
	nome_usuario,
	om,
	codom,
	sexo,
	cpf,
	qms,
	rm,
	cgcfex,
	data_inscricao_curso,
	termino_ultima_tentativa,
	total_tentativas,
	nota_final,
	16
order by
	nome_inscrito;
'''