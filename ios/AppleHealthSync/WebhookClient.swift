import Foundation
import AppleHealthSyncCore

struct WebhookResponse: Decodable, Sendable {
    let accepted: Int
    let ignored: Int
}

enum WebhookError: LocalizedError {
    case invalidURL
    case invalidResponse
    case http(status: Int, message: String)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Enter a valid webhook URL starting with http:// or https://."
        case .invalidResponse:
            return "Home Assistant returned a response the app could not read."
        case .http(let status, let message):
            if status == 401 {
                return "Home Assistant rejected the shared secret (HTTP 401)."
            }
            if status == 413 {
                return "Home Assistant rejected the payload as too large (HTTP 413)."
            }
            let body = message.trimmingCharacters(in: .whitespacesAndNewlines)
            return body.isEmpty
                ? "Home Assistant returned HTTP \(status)."
                : "Home Assistant returned HTTP \(status): \(body)"
        }
    }
}

struct WebhookClient {
    static func validateURL(_ string: String) -> URL? {
        let trimmed = string.trimmingCharacters(in: .whitespacesAndNewlines)
        guard let url = URL(string: trimmed),
              let scheme = url.scheme?.lowercased(),
              scheme == "http" || scheme == "https",
              let host = url.host,
              !host.isEmpty else {
            return nil
        }
        return url
    }

    func send(
        payload: HealthPayload,
        url: URL,
        secret: String
    ) async throws -> WebhookResponse {
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.timeoutInterval = 30
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        let trimmedSecret = secret.trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmedSecret.isEmpty {
            request.setValue(trimmedSecret, forHTTPHeaderField: "X-Webhook-Secret")
        }

        request.httpBody = try payload.encoded()

        let configuration = URLSessionConfiguration.ephemeral
        configuration.timeoutIntervalForRequest = 30
        configuration.timeoutIntervalForResource = 45
        let session = URLSession(configuration: configuration)
        defer { session.finishTasksAndInvalidate() }

        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw WebhookError.invalidResponse
        }

        guard (200..<300).contains(http.statusCode) else {
            let message = String(data: data, encoding: .utf8) ?? ""
            throw WebhookError.http(status: http.statusCode, message: message)
        }

        guard let decoded = try? JSONDecoder().decode(WebhookResponse.self, from: data) else {
            throw WebhookError.invalidResponse
        }
        return decoded
    }
}
