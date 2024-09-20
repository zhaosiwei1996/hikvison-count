// InfluxDB API settings
const INFLUXDB_URL = 'http://localhost/influxdb'; // Replace with your InfluxDB URL
const INFLUXDB_TOKEN = 'BLUnYl1EbFDUg-o8frrkkK2FzenGgIfwaT8IF_yHjN0w_HiS58dQI-Eke9ZAZ9z-Wz4McXIturdlf7QYe_Z_wA=='; // Replace with your InfluxDB token
const INFLUXDB_ORG = 'cmev'; // Replace with your organization name
const INFLUXDB_DATABASE = 'test'; // Replace with your database name

// Function to fetch data from InfluxDB using InfluxQL
async function fetchInfluxQLData(query) {
    const url = `${INFLUXDB_URL}/query`;
    const headers = {
        'Authorization': `Token ${INFLUXDB_TOKEN}`,
        'Content-Type': 'application/x-www-form-urlencoded'
    };
    const params = new URLSearchParams({ db: INFLUXDB_DATABASE, q: query });

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: params
        });

        if (!response.ok) {
            throw new Error(`Error fetching data from InfluxDB: ${response.statusText}`);
        }

        const json = await response.json();
        return parseInfluxQLResponse(json);
    } catch (error) {
        console.error(error);
        return [];
    }
}

// Function to parse InfluxQL JSON response
function parseInfluxQLResponse(json) {
    const results = [];

    if (!json.results || json.results.length === 0) return results;

    const series = json.results[0].series || [];
    series.forEach(({ columns, values }) => {
        const [timeIndex, entryIndex, exitIndex] = ['time', 'entry', 'exit'].map(field => columns.indexOf(field));

        values.forEach(value => {
            // Convert the timestamp to GMT+7
            const date = new Date(value[timeIndex]);
            const options = { timeZone: 'Asia/Bangkok', year: 'numeric', month: '2-digit', day: '2-digit' };
            const dateString = date.toLocaleDateString('zh-CN', options).replace(/\//g, '-');

            const entryValue = value[entryIndex];
            const exitValue = value[exitIndex];

            // Only add records with data
            if (entryValue !== null || exitValue !== null) {
                results.push({
                    date: dateString,
                    entry: entryValue !== null ? parseFloat(entryValue) : null,
                    exit: exitValue !== null ? parseFloat(exitValue) : null
                });
            }
        });
    });

    return results;
}

// Function to fetch and display daily last records
async function fetchDailyLastRecords() {
    const query = `
        SELECT LAST("entry") AS "entry", LAST("exit") AS "exit"
        FROM "entry_exit_metric"
        WHERE time >= now() - 30d
        GROUP BY time(1d)
    `;

    const data = await fetchInfluxQLData(query);

    // Log parsed data for debugging
    console.log('Parsed Data:', data);
    
    if (data && data.length > 0) {
        const tableBody = document.getElementById('daily-last-records');
        tableBody.innerHTML = ''; // Clear previous content
		data.sort((a, b) => new Date(b.date) - new Date(a.date));
        data.forEach(record => {
            // Only display records with data
            if (record.entry !== null || record.exit !== null) {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${record.date}</td>
                    <td>${record.entry !== null ? record.entry : '-'}</td>
                    <td>${record.exit !== null ? record.exit : '-'}</td>
                `;
                tableBody.appendChild(row);
            }
        });
    }
}

// Fetch data on page load
fetchDailyLastRecords();
