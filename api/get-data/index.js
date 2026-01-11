module.exports = async function (context, req) {
    context.log('Retrieving assessment data');
    
    try {
        // In production, this would retrieve from Azure Storage/Cosmos DB
        // For now, read from binding
        const data = context.bindings.inputData;
        
        if (!data) {
            context.res = {
                status: 404,
                body: { message: 'No data found. Please upload an assessment file first.' }
            };
            return;
        }
        
        const parsedData = typeof data === 'string' ? JSON.parse(data) : data;
        
        context.res = {
            status: 200,
            headers: {
                'Content-Type': 'application/json'
            },
            body: parsedData
        };
        
    } catch (error) {
        context.log.error('Error retrieving data:', error);
        context.res = {
            status: 500,
            body: { message: 'Error retrieving data: ' + error.message }
        };
    }
};
