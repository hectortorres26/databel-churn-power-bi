let
    Archivo = if Text.StartsWith(FuenteCSV, "https://") then Web.Contents(FuenteCSV) else File.Contents(FuenteCSV),
    CSV = Csv.Document(Archivo,[Delimiter=",", Columns=29, Encoding=1252, QuoteStyle=QuoteStyle.Csv]),
    Cabeceras = Table.PromoteHeaders(CSV, [PromoteAllScalars=true]),
    SinTelefono = Table.RemoveColumns(Cabeceras, {"Phone Number"}),
    Tipos = Table.TransformColumnTypes(SinTelefono, {{"Customer ID", type text}, {"Churn Label", type text}, {"Account Length (in months)", Int64.Type}, {"Local Calls", Int64.Type}, {"Local Mins", type number}, {"Intl Calls", Int64.Type}, {"Intl Mins", type number}, {"Intl Active", type text}, {"Intl Plan", type text}, {"Extra International Charges", Int64.Type}, {"Customer Service Calls", Int64.Type}, {"Avg Monthly GB Download", Int64.Type}, {"Unlimited Data Plan", type text}, {"Extra Data Charges", Int64.Type}, {"State", type text}, {"Gender", type text}, {"Age", Int64.Type}, {"Under 30", type text}, {"Senior", type text}, {"Group", type text}, {"Number of Customers in Group", Int64.Type}, {"Device Protection & Online Backup", type text}, {"Contract Type", type text}, {"Payment Method", type text}, {"Monthly Charge", Int64.Type}, {"Total Charges", Int64.Type}, {"Churn Category", type text}, {"Churn Reason", type text}}, "en-US"),
    Edades = Table.AddColumn(Tipos, "Grupo de edad", each if [Age] < 30 then "Menores de 30" else if [Age] >= 65 then "65 o más" else "30 a 64", type text),
    Categorias = Table.AddColumn(Edades, "Categoria de abandono", each if [Churn Label] <> "Yes" then "No aplica" else if [Churn Category] = null or Text.Trim([Churn Category]) = "" then "Sin motivo informado" else [Churn Category], type text),
    Motivos = Table.AddColumn(Categorias, "Motivo de abandono", each if [Churn Label] <> "Yes" then "No aplica" else if [Churn Reason] = null or Text.Trim([Churn Reason]) = "" then "Sin motivo informado" else [Churn Reason], type text)
in
    Motivos
