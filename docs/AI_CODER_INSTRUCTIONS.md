# AI Coder Instructions for Garden Database

This document provides detailed instructions for AI code agents on how to access and use the Garden Database in other projects. It covers API endpoints, authentication, data structures, and includes example code for common operations.

## Overview

The Garden Database provides comprehensive information about plants, companion planting relationships, pests, diseases, fertilizers, and more. You can access this data through:

1. **REST API** - For standard CRUD operations
2. **GraphQL API** - For flexible, customized queries
3. **Direct Database Access** - For applications running in the same environment

## Authentication

### REST API Authentication

The API uses token-based authentication. To access protected endpoints:

1. **Obtain a token**:

```python
import requests

url = "http://localhost:8000/api/v1/auth/token/"
data = {
    "username": "your_username",
    "password": "your_password"
}
response = requests.post(url, data=data)
token = response.json()["token"]
```

2. **Use the token in subsequent requests**:

```python
headers = {
    "Authorization": f"Token {token}"
}
response = requests.get("http://localhost:8000/api/v1/plants/", headers=headers)
```

### GraphQL Authentication

GraphQL uses the same token authentication:

```python
import requests

url = "http://localhost:8000/graphql"
headers = {
    "Authorization": f"Token {token}",
    "Content-Type": "application/json"
}
query = """
{
  allPlants {
    edges {
      node {
        id
        commonName
        scientificName
      }
    }
  }
}
"""
response = requests.post(url, json={"query": query}, headers=headers)
```

## REST API Endpoints

### Base URL

The base URL for the API is: `http://localhost:8000/api/v1/`

### Available Endpoints

| Endpoint | Description | Methods |
|----------|-------------|---------|
| `/plants/` | List or create plants | GET, POST |
| `/plants/{id}/` | Retrieve, update or delete a plant | GET, PUT, PATCH, DELETE |
| `/seeds/` | List or create seeds | GET, POST |
| `/seeds/{id}/` | Retrieve, update or delete a seed | GET, PUT, PATCH, DELETE |
| `/pests/` | List or create pests | GET, POST |
| `/pests/{id}/` | Retrieve, update or delete a pest | GET, PUT, PATCH, DELETE |
| `/diseases/` | List or create diseases | GET, POST |
| `/diseases/{id}/` | Retrieve, update or delete a disease | GET, PUT, PATCH, DELETE |
| `/companionships/` | List or create companion relationships | GET, POST |
| `/companionships/{id}/` | Retrieve, update or delete a companionship | GET, PUT, PATCH, DELETE |
| `/fertilizers/` | List or create fertilizers | GET, POST |
| `/fertilizers/{id}/` | Retrieve, update or delete a fertilizer | GET, PUT, PATCH, DELETE |
| `/regions/` | List or create regions | GET, POST |
| `/regions/{id}/` | Retrieve, update or delete a region | GET, PUT, PATCH, DELETE |
| `/soil-profiles/` | List or create soil profiles | GET, POST |
| `/soil-profiles/{id}/` | Retrieve, update or delete a soil profile | GET, PUT, PATCH, DELETE |
| `/horticulture/plants/{plant_id}/compatibility/` | Retrieve compatibility details for a plant | GET |


#### Plant Compatibility Endpoint (`/horticulture/plants/{plant_id}/compatibility/`)

Retrieves comprehensive compatibility data for a specific plant identified by `{plant_id}`. This includes the plant's own pH range and details about its companion plants (beneficial, detrimental, neutral).

**Method:** `GET`

**URL Parameters:**
*   `{plant_id}` (uuid): The unique identifier of the plant for which to retrieve compatibility data.

**Example Response:**

```json
{
  "plant_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "common_name": "Tomato",
  "scientific_name": "Solanum lycopersicum",
  "soil_ph_min": "6.0",
  "soil_ph_max": "6.8",
  "compatible_companions": [
    {
      "plant_id": "b2c3d4e5-f6a7-8901-2345-67890abcdef1",
      "common_name": "Basil",
      "scientific_name": "Ocimum basilicum",
      "interaction_type": "BEN",
      "mechanism_description": "Repels tomato hornworms and whiteflies."
    },
    {
      "plant_id": "c3d4e5f6-a7b8-9012-3456-7890abcdef12",
      "common_name": "Carrot",
      "scientific_name": "Daucus carota",
      "interaction_type": "BEN",
      "mechanism_description": "Loosens soil."
    }
  ],
  "incompatible_companions": [
    {
      "plant_id": "d4e5f6a7-b8c9-0123-4567-890abcdef123",
      "common_name": "Fennel",
      "scientific_name": "Foeniculum vulgare",
      "interaction_type": "DET",
      "mechanism_description": "Inhibits tomato growth."
    }
  ],
  "neutral_companions": []
}
```

### Filtering and Searching

Most endpoints support filtering and searching:

```python
# Get all annual plants
response = requests.get("http://localhost:8000/api/v1/plants/?lifecycle_type=AN", headers=headers)

# Search plants by name
response = requests.get("http://localhost:8000/api/v1/plants/?search=tomato", headers=headers)

# Filter plants by family
response = requests.get("http://localhost:8000/api/v1/plants/?family=Solanaceae", headers=headers)
```

## GraphQL API

### Endpoint

The GraphQL endpoint is: `http://localhost:8000/graphql`

### Example Queries

**Get plants with their companion relationships**:

```graphql
{
  allPlants {
    edges {
      node {
        id
        commonName
        scientificName
        companionshipsAsSubject {
          edges {
            node {
              plantObject {
                commonName
              }
              interactions {
                edges {
                  node {
                    interactionType
                    mechanismDescription
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

**Get pests with affected plants**:

```graphql
{
  allPests {
    edges {
      node {
        commonName
        scientificName
        plants {
          edges {
            node {
              commonName
              scientificName
            }
          }
        }
      }
    }
  }
}
```

## Data Models

Understanding the data models is crucial for effective API usage:

### Plant

```json
{
  "id": "uuid",
  "common_name": "String",
  "scientific_name": "String",
  "description": "String",
  "family": "String",
  "genus": "String",
  "species": "String",
  "lifecycle_type": "String (AN/PE/BI)",
  "growth_habit": "String (VI/SH/TR/GC/HB/BU)",
  "avg_height_inches": "Integer",
  "avg_spread_inches": "Integer",
  "days_to_maturity_min": "Integer",
  "days_to_maturity_max": "Integer",
  "sunlight_requirements": "String (FS/PS/SH/FD)",
  "moisture_requirements": "String (LO/MO/HI/BO)",
  "soil_ph_min": "Decimal",
  "soil_ph_max": "Decimal"
}
```

### Companionship

```json
{
  "id": "uuid",
  "plant_subject": "Plant UUID",
  "plant_object": "Plant UUID",
  "notes": "String",
  "interactions": [
    {
      "interaction_type": "String (BEN/DET/NEU)",
      "mechanism_description": "String"
    }
  ]
}
```

### Pest

```json
{
  "id": "uuid",
  "common_name": "String",
  "scientific_name": "String",
  "description": "String",
  "category": "String (INS/MAM/MOL/OTH)",
  "symptoms": "String",
  "damage_type": "String",
  "severity_level": "String (LOW/MED/HIG)",
  "control_methods": "String",
  "plants": ["Plant UUID"]
}
```

For complete data models, refer to the [DATA_MODEL.md](DATA_MODEL.md) file.

## Code Examples

### Example 1: Get Plants and Their Companions

```python
import requests

def get_plants_with_companions(base_url, token):
    headers = {"Authorization": f"Token {token}"}
    
    # Get all plants
    plants_response = requests.get(f"{base_url}/api/v1/plants/", headers=headers)
    plants = plants_response.json()
    
    result = []
    
    for plant in plants["results"]:
        plant_id = plant["id"]
        
        # Get companionships where this plant is the subject
        companions_response = requests.get(
            f"{base_url}/api/v1/companionships/?plant_subject={plant_id}",
            headers=headers
        )
        companions = companions_response.json()
        
        plant_data = {
            "plant": plant,
            "companions": companions["results"]
        }
        
        result.append(plant_data)
    
    return result

# Usage
base_url = "http://localhost:8000"
token = "your_auth_token"
plants_with_companions = get_plants_with_companions(base_url, token)
```

### Example 2: Find Plants Suitable for Specific Conditions

```python
import requests

def find_suitable_plants(base_url, token, sunlight, moisture, min_ph, max_ph):
    headers = {"Authorization": f"Token {token}"}
    
    # Build query parameters
    params = {
        "sunlight_requirements": sunlight,
        "moisture_requirements": moisture,
        "soil_ph_min__lte": min_ph,
        "soil_ph_max__gte": max_ph
    }
    
    response = requests.get(f"{base_url}/api/v1/plants/", params=params, headers=headers)
    return response.json()

# Usage
base_url = "http://localhost:8000"
token = "your_auth_token"
suitable_plants = find_suitable_plants(base_url, token, "FS", "MO", 6.0, 7.0)
```

### Example 3: Get Pest Control Information for a Plant

```python
import requests

def get_pest_control_for_plant(base_url, token, plant_scientific_name):
    headers = {"Authorization": f"Token {token}"}
    
    # Get plant ID
    plant_response = requests.get(
        f"{base_url}/api/v1/plants/?scientific_name={plant_scientific_name}",
        headers=headers
    )
    plants = plant_response.json()
    
    if not plants["results"]:
        return {"error": "Plant not found"}
    
    plant_id = plants["results"][0]["id"]
    
    # Get pests that affect this plant
    pests_response = requests.get(
        f"{base_url}/api/v1/pests/?plants={plant_id}",
        headers=headers
    )
    
    return {
        "plant": plants["results"][0],
        "pests": pests_response.json()["results"]
    }

# Usage
base_url = "http://localhost:8000"
token = "your_auth_token"
pest_info = get_pest_control_for_plant(base_url, token, "Solanum lycopersicum")
```

## Using the Database in Different Programming Languages

### JavaScript/Node.js

```javascript
const axios = require('axios');

async function getPlants(baseUrl, token) {
  try {
    const response = await axios.get(`${baseUrl}/api/v1/plants/`, {
      headers: {
        'Authorization': `Token ${token}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching plants:', error);
    return null;
  }
}

// Usage
const baseUrl = 'http://localhost:8000';
const token = 'your_auth_token';
getPlants(baseUrl, token).then(plants => console.log(plants));
```

### Ruby

```ruby
require 'net/http'
require 'json'

def get_plants(base_url, token)
  uri = URI("#{base_url}/api/v1/plants/")
  request = Net::HTTP::Get.new(uri)
  request['Authorization'] = "Token #{token}"
  
  response = Net::HTTP.start(uri.hostname, uri.port) do |http|
    http.request(request)
  end
  
  JSON.parse(response.body)
end

# Usage
base_url = 'http://localhost:8000'
token = 'your_auth_token'
plants = get_plants(base_url, token)
puts plants
```

### Go

```go
package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

func getPlants(baseURL, token string) (map[string]interface{}, error) {
	client := &http.Client{}
	req, err := http.NewRequest("GET", baseURL+"/api/v1/plants/", nil)
	if err != nil {
		return nil, err
	}
	
	req.Header.Add("Authorization", "Token "+token)
	
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	
	var result map[string]interface{}
	err = json.Unmarshal(body, &result)
	if err != nil {
		return nil, err
	}
	
	return result, nil
}

// Usage
// baseURL := "http://localhost:8000"
// token := "your_auth_token"
// plants, err := getPlants(baseURL, token)
```

## Best Practices

1. **Cache Responses**: Many garden database queries return data that doesn't change frequently. Consider caching responses to reduce API calls.

2. **Batch Requests**: When possible, retrieve multiple items in a single request rather than making separate requests for each item.

3. **Use Pagination**: The API returns paginated results. Make sure to handle pagination by following the `next` URL in the response.

4. **Handle Errors Gracefully**: Always check for error responses and handle them appropriately in your application.

5. **Use GraphQL for Complex Queries**: If you need data from multiple related entities, consider using GraphQL instead of making multiple REST API calls.

6. **Respect Rate Limits**: The API may have rate limits. Implement exponential backoff if you encounter rate limit errors.

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure your token is valid and properly formatted in the Authorization header.

2. **Not Found Errors**: Check that the IDs or parameters you're using exist in the database.

3. **Validation Errors**: When creating or updating records, ensure all required fields are provided and in the correct format.

### Getting Help

If you encounter issues not covered in this document, you can:

1. Check the API documentation at `http://localhost:8000/api/docs/`
2. Examine the GraphQL schema at `http://localhost:8000/graphql`
3. Refer to the [DATA_MODEL.md](DATA_MODEL.md) file for detailed information about data structures

## Conclusion

The Garden Database provides a rich set of data and flexible APIs that can be integrated into various applications. Whether you're building a gardening app, a plant identification tool, or a companion planting advisor, the database offers the information you need in accessible formats.

By following these instructions, AI code agents should be able to effectively access and utilize the Garden Database in their projects.
