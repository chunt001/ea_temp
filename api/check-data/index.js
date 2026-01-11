module.exports = async function (context, req) {
    context.log('Checking for existing data');
    
    try {
        const data = context.bindings.inputData;
        
        context.res = {
            status: 200,
            headers: {
                'Content-Type': 'application/json'
            },
            body: {
                hasData: !!data
            }
        };
        
    } catch (error) {
        context.log.error('Error checking data:', error);
        context.res = {
            status: 200,
            body: { hasData: false }
        };
    }
};
