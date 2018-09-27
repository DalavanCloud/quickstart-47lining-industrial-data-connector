import apiClient, { sendForm } from './shared/apiClient'

apiClient.interpolateFeeds =  payload => {
    return sendForm('/api/v1/feeds/interpolate', payload, 'Interpolation request sent', 'Cannot send interpolation request');
}

export default apiClient
