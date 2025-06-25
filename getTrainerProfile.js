const axios = require('axios');
const fs = require('fs');
const path = require('path');
// const XLSX = require('xlsx');

// Configuration
const GRAPHQL_URL = "https://graphql.rmdprod.racing.com/";
const API_KEY = "da2-6nsi4ztsynar3l3frgxf77q5fe";
// const EXCEL_FILE_PATH = path.join(__dirname, "HorseData.xlsx");
const OUTPUT_DIR = path.join(__dirname, "results");
const IDS_FILE_PATH = path.join(__dirname, "ids/trainerProfileID.json"); // Path to your IDs file
const DELAY_BETWEEN_REQUESTS_MS = 100;

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR);
}

// Create output file
const outputFilePath = path.join(OUTPUT_DIR, `matched_trainers_${Date.now()}.json`);
fs.writeFileSync(outputFilePath, JSON.stringify([], null, 2));

// Load trainer IDs from JSON file
function loadTrainerIds() {
    try {
        console.log(`Loading trainer IDs from: ${IDS_FILE_PATH}`);
        const data = fs.readFileSync(IDS_FILE_PATH);
        return JSON.parse(data);
    } catch (error) {
        console.error("Failed to load IDs file:", error);
        process.exit(1);
    }
}

// Load trainer data from Excel
// function loadTrainerData() {
//     try {
//         console.log(`Loading Excel data from: ${EXCEL_FILE_PATH}`);
//         // const workbook = XLSX.readFile(EXCEL_FILE_PATH);
//         const sheet = workbook.Sheets[workbook.SheetNames[0]];
//         // const data = XLSX.utils.sheet_to_json(sheet);
        
//         return data.map(row => ({
//             name: row['Trainer name']?.toString().trim(),
//             location: row['Location']?.toString().trim(),
//             price: row['Price']
//         })).filter(trainer => trainer.name && trainer.location && trainer.price !== undefined);
//     } catch (error) {
//         console.error("Failed to load Excel file:", error);
//         process.exit(1);
//     }
// }

// Fetch trainer profile
async function getTrainerProfile(trainerId) {
    
    const query = `
    query getTrainerProfile($id: ID!) {
        getTrainerProfile(id: $id) {
            id
            sitecoreId
            location
            fullName
            careerWins
            group1Wins
            winPercent
            placePercent
            based
            prizeMoney
            recentWinPercent
            firstWinRaceEntryItem {
                id
                horseName
                raceDate
                __typename
            }
            __typename
        }
    }
    `;
    
    try {
        const response = await axios.post(GRAPHQL_URL, {
            query,
            variables: { id: trainerId }
        }, {
            headers: {
                "Content-Type": "application/json",
                "x-api-key": API_KEY
            }
        });
        return response.data?.data?.getTrainerProfile || null;
    } catch (error) {
        console.error(`Error fetching ${trainerId}:`, error.message);
        return null;
    }
}

// Check if profile matches our criteria
function isMatchingProfile(profile, trainerData) {
    if (!profile || !profile.fullName || !profile.location) return false;
    
    return trainerData.some(trainer => 
        trainer.name === profile.fullName && 
        trainer.location === profile.location
    );
}

// Get matching trainer data from Excel
function getMatchingTrainerData(profile, trainerData) {
    return trainerData.find(trainer => 
        trainer.name === profile.fullName && 
        trainer.location === profile.location
    );
}

// Save matched profiles
function saveMatchedProfile(profile, trainerData) {
    const matchedData = getMatchingTrainerData(profile, trainerData);
    const enrichedProfile = {
        ...profile,
        price: matchedData.price,
        excelData: {
            location: matchedData.location,
            expectedPrice: matchedData.price
        }
    };
    
    const currentData = JSON.parse(fs.readFileSync(outputFilePath));
    currentData.push(enrichedProfile);
    fs.writeFileSync(outputFilePath, JSON.stringify(currentData, null, 2));
}

// Main function
async function main() {
    const trainerIds = loadTrainerIds();
    
    // const trainerData = loadTrainerData();
    
    console.log(`Loaded ${trainerIds.length} trainer IDs from JSON file`);
    // console.log(`Loaded ${trainerData.length} trainer records from Excel`);
    
    let matchedCount = 0;
    
    for (let i = 0; i < trainerIds.length / 2; i++) {
        const trainerId = trainerIds[i].toString();
        console.log(`Processing ID ${i + 1}/${trainerIds.length}: ${trainerId}`);
        
        const profile = await getTrainerProfile(trainerId);
        const currentData = JSON.parse(fs.readFileSync(outputFilePath));
        currentData.push(profile);
        fs.writeFileSync(outputFilePath, JSON.stringify(currentData, null, 2));
        // console.log(trainerId);
        // console.log(profile)
        
        // if (isMatchingProfile(profile, trainerData)) {
        //     saveMatchedProfile(profile, trainerData);
        //     matchedCount++;
        //     console.log(`✅ MATCHED: ${profile.fullName} (${trainerId}) - Location: ${profile.location}`);
        // }
        
        // Progress reporting
        if (i % 100 === 0) {
            console.log(`Progress: ${((i + 1) / trainerIds.length * 100).toFixed(2)}% | Matched: ${matchedCount}`);
        }
        
        // Rate limiting
        await new Promise(resolve => setTimeout(resolve, DELAY_BETWEEN_REQUESTS_MS));
    }
    
    console.log(`\nScan complete! Found ${matchedCount} matching trainers.`);
    console.log(`Results saved to: ${outputFilePath}`);
}

main().catch(console.error);