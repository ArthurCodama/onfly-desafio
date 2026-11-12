# Entrega — consolidador de reservas

## Defeitos e causas raiz

| Commit | Correção | Causa raiz |
| --- | --- | --- |
| `3b2f686` | Ler todas as reservas | O repositório interrompia a leitura ao atingir 200 registros. |
| `ed71742` | Calcular noites com datas completas | A subtração usava somente o dia do mês, ignorando mês e ano. |
| `057f1c9` | Converter moedas com multiplicação Decimal | A conversão dividia pela taxa e passava por float, invertendo o câmbio e perdendo precisão. |
| `3a8aaf0` | Faturar somente CONFIRMED | O predicado excluía apenas CANCELLED e incluía NO_SHOW nas agregações. |
| `ff318b6` | Ordenar hotéis por valor decrescente | A ordenação usava o valor crescente, retornando primeiro os hotéis de menor total. |

Cada correção está em um commit separado com seus testes de regressão. Não foram alterados os testes fornecidos, os CSVs, os argumentos ou o schema público.

## Investigação e abordagem

Li as regras do README, os serviços, os repositórios CSV e os testes fornecidos. Após instalar as dependências, executei os cinco testes originais: **5 failed**. Antes das correções, os novos testes de regressão também reproduziram as falhas: **14 failed, 8 passed**.

As correções foram pequenas e localizadas, mantendo a arquitetura existente. Cada grupo de testes foi executado após sua correção e antes de criar o commit correspondente. Dinheiro continua em Decimal até a serialização half-up; o ranking compara valores exatos antes de arredondar.

A cobertura adicional verifica os limites 199/200/201/300 registros, viradas de mês/ano, ano bissexto, múltiplos quartos, estadia sem noites, centavos fracionários, média sem arredondamento intermediário, status não faturáveis, entrada vazia, desempate por hotel e limites do ranking. Testes de contrato cobrem a amostra completa, offset -03:00, saída padrão, criação de diretórios, argumentos inválidos e códigos de saída 0/1/2.

## Como validar

Requer Python >= 3.11. Na raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
ruff check src tests
git diff --check
PYTHONPATH=src python -m onfly_report --input data/exemplo-validacao.csv --rates data/taxas_cambio.csv --output output/exemplo.json
PYTHONPATH=src python -m onfly_report --input data/reservas_hoteis.csv --rates data/taxas_cambio.csv --output output/report.json
```

Resultado observado: **38 passed in 10.53s**, com pytest 8.3.4 e Python **3.12.3**. Ruff 0.8.4: **All checks passed!**; `git diff --check`: sem erros. Python 3.11 não está instalado neste ambiente, portanto a execução nessa versão não foi validada.

A amostra coincide integralmente com os valores esperados no README: 12 reservas, 9 confirmadas, 2 canceladas, 1 no-show, 28 noites, total BRL 7566.00, média BRL 270.21, além dos meses e cinco hotéis esperados.

Dataset principal: 300 reservas, 235 confirmadas, 31 canceladas, 34 no-show, 1347 noites, total BRL 396170.00 e média BRL 294.11. Os relatórios gerados ficam em `output/`, ignorado pelo Git.

## Entrega local e uso de IA

Esta entrega inclui código, testes e documentação local. A publicação do repositório e o envio do formulário ficam a cargo do responsável pela entrega.

O registro consolidado de prompts/respostas está em `uso-de-ia/sessao.md`; ferramenta e responsabilidades estão em `uso-de-ia/declaracao.md`.
