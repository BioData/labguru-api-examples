using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using CsvHelper;
using CsvHelper.Configuration;
using Newtonsoft.Json;

namespace LabguruAPIExample
{
    public class CsvRecord
    {
        public string? field_name { get; set; }
        public string? type { get; set; }
        public string? min { get; set; }
        public string? max { get; set; }
        public string? hint { get; set; }
        public int row { get; set; }
    }

    public sealed class CsvRecordMap : ClassMap<CsvRecord>
    {
        public CsvRecordMap()
        {
            Map(m => m.field_name).Name("field_name");
            Map(m => m.type).Name("type");
            Map(m => m.min).Name("min");
            Map(m => m.max).Name("max");
            Map(m => m.hint).Name("hint");
            Map(m => m.row).Name("row");
        }
    }

    class Program
    {
        private static readonly string apiKey = "YOUR_API_KEY_HERE";
        private static readonly string apiUrl = "YOUR_API_URL_HERE";

        static async Task Main(string[] args)
        {
            if (args.Length < 1)
            {
                Console.WriteLine("Please provide the CSV file path as an argument.");
                return;
            }

            var csvFilePath = args[0];
            var csvRecords = ReadCsvFile(csvFilePath);

            var protocol = new
            {
                name = "New Protocol",
                description = "This is a sample protocol"
            };

            var protocolId = await AddProtocolAsync(protocol);

            if (!string.IsNullOrEmpty(protocolId))
            {
                var procedure = new
                {
                    item = new
                    {
                        container_type = "Knowledgebase::Protocol",
                        container_id = protocolId,
                        name = "Report Form",
                        position = 1
                    }
                };

                var sectionId = await AddProcedureAsync(procedure, protocolId);

                if (!string.IsNullOrEmpty(sectionId))
                {
                    var htmlTable = GenerateHtmlTable(csvRecords);
                    var formJson = GenerateFormJson(csvRecords);

                    await AddFormElementAsync(sectionId, htmlTable, formJson);
                }
            }
        }

        private static List<CsvRecord> ReadCsvFile(string filePath)
        {
            using (var reader = new StreamReader(filePath))
            using (var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HeaderValidated = null,
                MissingFieldFound = null,
                PrepareHeaderForMatch = args => args.Header.Trim().ToLower()
            }))
            {
                csv.Context.RegisterClassMap<CsvRecordMap>();
                return new List<CsvRecord>(csv.GetRecords<CsvRecord>());
            }
        }

        private static string GenerateHtmlTable(List<CsvRecord> records)
        {
            var html = new StringBuilder();
            html.Append("<table style='width: 100%;'><tbody>");

            foreach (var rowGroup in records.GroupBy(r => r.row))
            {
                html.Append("<tr>");
                foreach (var record in rowGroup)
                {
                    html.AppendFormat("<td style='width: 25.0000%;'>{0}</td>", record.hint);
                    html.AppendFormat("<td style='width: 25.0000%;'><input disabled='' class='form-control' name='{0}' title='{1}' type='{2}' placeholder='{0}' {3} {4}></td>",
                        record.field_name,
                        "Cannot add values to fields in protocols. To add values, start an experiment from the protocol",
                        record.type,
                        record.type == "number" && !string.IsNullOrEmpty(record.min) ? $"min='{record.min}'" : "",
                        record.type == "number" && !string.IsNullOrEmpty(record.max) ? $"max='{record.max}'" : ""
                    );
                }
                html.Append("</tr>");
            }

            html.Append("</tbody></table><p><br></p>");
            return html.ToString();
        }

        private static string GenerateFormJson(List<CsvRecord> records)
        {
            var questions = new List<object>();

            foreach (var record in records)
            {
                var questionData = new List<Dictionary<string, string>>();
                if (!string.IsNullOrEmpty(record.min))
                {
                    questionData.Add(new Dictionary<string, string> { { "min", record.min } });
                }
                if (!string.IsNullOrEmpty(record.max))
                {
                    questionData.Add(new Dictionary<string, string> { { "max", record.max } });
                }

                questions.Add(new
                {
                    question = record.field_name,
                    question_type = record.type,
                    question_data = questionData
                });
            }

            var formJson = new
            {
                form_json = new { questions = questions }
            };

            return JsonConvert.SerializeObject(formJson);
        }

        private static async Task<string> AddProtocolAsync(object protocol)
        {
            using (var client = new HttpClient())
            {
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");

                var json = JsonConvert.SerializeObject(protocol);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await client.PostAsync($"{apiUrl}/protocols?token={apiKey}", content);

                if (response.IsSuccessStatusCode)
                {
                    var responseBody = await response.Content.ReadAsStringAsync();
                    dynamic result = JsonConvert.DeserializeObject(responseBody);
                    Console.WriteLine("Protocol added successfully.");
                    return result.id;
                }
                else
                {
                    var responseBody = await response.Content.ReadAsStringAsync();
                    Console.WriteLine($"Error: {response.StatusCode}, Details: {responseBody}");
                    return null;
                }
            }
        }

        private static async Task<string> AddProcedureAsync(object procedure, string protocolId)
        {
            using (var client = new HttpClient())
            {
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");

                var json = JsonConvert.SerializeObject(procedure);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await client.PostAsync($"{apiUrl}/sections?token={apiKey}", content);

                if (response.IsSuccessStatusCode)
                {
                    var responseBody = await response.Content.ReadAsStringAsync();
                    dynamic result = JsonConvert.DeserializeObject(responseBody);
                    Console.WriteLine("Procedure added successfully.");
                    return result.id;
                }
                else
                {
                    var responseBody = await response.Content.ReadAsStringAsync();
                    Console.WriteLine($"Error: {response.StatusCode}, Details: {responseBody}");
                    return null;
                }
            }
        }

        private static async Task AddFormElementAsync(string sectionId, string htmlTable, string formJson)
        {
            using (var client = new HttpClient())
            {
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");

                var formElement = new
                {
                    item = new
                    {
                        name = "Sample Manager",
                        element_type = "form",
                        data = htmlTable,
                        container_type = "ExperimentProcedure",
                        container_id = sectionId,
                        description = formJson,
                        is_valid = false
                    }
                };

                var json = JsonConvert.SerializeObject(formElement);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await client.PostAsync($"{apiUrl}/elements?token={apiKey}", content);

                if (response.IsSuccessStatusCode)
                {
                    Console.WriteLine("Form element added successfully.");
                }
                else
                {
                    var responseBody = await response.Content.ReadAsStringAsync();
                    Console.WriteLine($"Error: {response.StatusCode}, Details: {responseBody}");
                }
            }
        }
    }
}
