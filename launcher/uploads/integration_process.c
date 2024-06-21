/*
 * Programmer   : Regis Rodolfo Schuch
 * Date         : 10 June 2024
 *              : Applied Computing Research Group, Unijui University, Brazil
 *              : regis.schuch@unijui.edu.br
 *              :
 * Title        : integration_process.c 
 *              :
 * Description  : The flow of communication between integration_process and the APIs is as follows:
 *              : 1) Start the Integration Process:
 *              :    a) The Integration_Process component is running on a TEE with CHERI architecture 
 *              :       on a Morello Board.
 *              : 2) Check Last Sale:
 *              :    a) Integration_Process calls the check_last_sale() function to check the last sale 
 *              :       in the Sales API (API1).
 *              :    b) The check_last_sale() function sends a GET request to the URL 1200.17.87.181:8080/api/vendas 
 *              :       (defined as API1_URL and API1_PORT), obtaining the last sale data.
 *              :    c) The function processes the data received for subsequent analysis, using functions 
 *              :       such as extract_total_value(), extract_client_address() and extract_client_phone() 
 *              :       to extract information specific to the sale.
 *              : 3) Analyse sales data:
 *              :    a) Integration_Process analyses the sale data using the parse_last_sale() function.
 *              :    b) The parse_last_sale() function extracts and processes the relevant information 
 *              :       from the last sale, such as the total amount, address and telephone number of 
 *              :       the customer.
 *              : 4) Get a Confirmation Message for the Trip:
 *              :    a) The Integration_Process calls the get_travel_confirmation_message() function to 
 *              :       obtain the journey confirmation message from the Travel API (API2).
 *              :    b) The get_travel_confirmation_message() function sends a GET request to the 
 *              :       URL 200.17.87.182:8080/api/viagens (defined as API2_URL and API2_PORT), obtaining 
 *              :       the trip confirmation message.
 *              : 5) Booking a trip:
 *              :    a) If the sale fulfils the criterion (value >= 150.00) for scheduling the trip, 
 *              :       Integration_Process calls the schedule_trip() function to schedule the trip 
 *              :       in the Travel API (API2).
 *              :    b) The schedule_trip() function receives as parameters the customer's address, 
 *              :       the customer's telephone number and the total amount of the last sale. It sends 
 *              :       a POST request to the URL 200.17.87.182:8080/api/viagens (defined as API2_URL 
 *              :       and API2_PORT), with the trip data in the body of the request.
 *              : 6) Send a confirmation message via WhatsApp:
 *              :    a) Integration_Process calls the send_message_confirmation_whatsapp() function to 
 *              :       send the confirmation message via WhatsApp to the customer.
 *              :    b) The send_message_confirmation_whatsapp() function receives the client's phone 
 *              :       number and the message to be sent as parameters. It sends a POST request to the 
 *              :       URL 200.17.87.183:8080/send-message (defined as API3_URL and API3_PORT), with 
 *              :       the message data in the body of the request.
 *              : 7) Conclude the Integration Process:
 *              :    a) Integration_Process completes the process and returns a response to the user.
 *              : 
 *              : This flow describes how the integration process code interacts with the APIs to verify 
 *              : sales, book trips and send confirmation messages, demonstrating a continuous process 
 *              : of integration and automation between different digital services.
 *              : 
 * Source       : Some inspiration from
 *              : https://www.cheribsd.org/tutorial/23.11/c18n/index.html
 *              : https://beej.us/guide/bgnet/pdf/bgnet_a4_c_1.pdf
 *              : https://curl.se/libcurl/c/libcurl-tutorial.html
 *              : https://curl.se/libcurl/c/CURLOPT_WRITEFUNCTION.html
 *              : https://everything.curl.dev/transfers/callbacks/write.html
 *              : https://www.geeksforgeeks.org/cjson-json-file-write-read-modify-in-c/
 *              : https://hayageek.com/cjson-examples-parse-write-print-json-with-cjson-in-c/
 *              : https://opensource.com/article/19/6/cryptography-basics-openssl-part-1
 *              : https://wiki.openssl.org/index.php/Simple_TLS_Server
 *              : https://www.cin.ufpe.br/~rngs/Arquivos/pthreads/pthreads.pdf
 *              :
 * Compile      :  
 * normal       : clang -o integration_process integration_process.c -lssl -lcrypto -lpthread
 *              :
 * Run          : ./integration_process 
 *              :
 *              :
 * Compile      :
 * Capabilities : clang-morello -march=morello+c64 -mabi=purecap -g -o integration_process integration_process.c -L. -Wl,-dynamic-linker,/libexec/ld-elf-c18n.so.1 -lssl -lcrypto -lpthread
 *              :
 * run          : env LD_C18N_LIBRARY_PATH=. ./integration_process	 
 * 
 * 
*/
// Include standard C libraries. It was not possible to use specific libraries because they do not support CHERI.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <time.h>
#include <openssl/ssl.h>
#include <openssl/err.h>

// Define URLs and ports for APIs
/* IP addresses are used directly because a memory allocation error occurs in the execution for CHERI capabilities 
when using DNS. */

#define API1_URL "200.17.87.181" // It's the IP address of: gca-vm-4.unijui.edu.br
#define API1_PORT "8080"
#define API1_ENDPOINT "/api/vendas"

#define API2_URL "200.17.87.182" // It's the IP address of: gca-vm-5.unijui.edu.br
#define API2_PORT "8080"
#define API2_ENDPOINT "/api/viagens"

#define API3_URL "200.17.87.183" // It's the IP address of: gca-vm-6.unijui.edu.br
#define API3_PORT "8080"
#define API3_ENDPOINT "/send-message" 

/*
#define API1_URL "127.0.0.1"
#define API1_PORT "8000"
#define API1_ENDPOINT "/api/vendas"

#define API2_URL "127.0.0.1"
#define API2_PORT "8001"
#define API2_ENDPOINT "/api/viagens"

#define API3_URL "127.0.0.1"
#define API3_PORT "9000"
#define API3_ENDPOINT "/send-message"
*/

// Function prototypes
void schedule_trip(const char *endereco_cliente, const char *telefone_cliente, double valor_total);
void get_travel_confirmation_message();
void check_last_sale();
void send_message_confirmation_whatsapp(const char *number, const char *message);
double extract_total_value(const char *data);
char *extract_client_address(const char *data);
char *extract_client_phone(const char *data);
void parse_last_sale();
void cleanup_ssl(SSL *ssl, SSL_CTX *ctx);

char *last_sale = NULL;
size_t last_sale_size = 0;
char *last_printed_sale = NULL;

// Variables for synchronisation control
pthread_mutex_t keys_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t keys_cond = PTHREAD_COND_INITIALIZER;
int keys_generated = 0;

SSL_CTX *initialize_ssl_context() {
    const SSL_METHOD *method;
    SSL_CTX *ctx;

    // Initialises the OpenSSL library
    OpenSSL_add_all_algorithms();
    SSL_load_error_strings();
    method = TLS_client_method();
    ctx = SSL_CTX_new(method);

    if (ctx == NULL) {
        ERR_print_errors_fp(stderr);
        abort();
    }

    // Paths to the certificate and private key files
    const char *cert_file = "/home/regis/NB-LOCAL-attestable/launcher/keys/cert.pem";
    const char *key_file = "/home/regis/NB-LOCAL-attestable/launcher/keys/prk.pem";

    // Verifica a existência dos arquivos
    if (access(cert_file, F_OK) == -1) {
        fprintf(stderr, "Certificate file not found: %s\n", cert_file);
        abort();
    }

    if (access(key_file, F_OK) == -1) {
        fprintf(stderr, "Private key file not found: %s\n", key_file);
        abort();
    }

    // Upload the certificate and private key files
    if (SSL_CTX_use_certificate_file(ctx, cert_file, SSL_FILETYPE_PEM) <= 0) {
        ERR_print_errors_fp(stderr);
        abort();
    }

    if (SSL_CTX_use_PrivateKey_file(ctx, key_file, SSL_FILETYPE_PEM) <= 0) {
        ERR_print_errors_fp(stderr);
        abort();
    }

    return ctx;
}

void cleanup_ssl(SSL *ssl, SSL_CTX *ctx) {
    if (ssl) {
        SSL_shutdown(ssl);
        SSL_free(ssl);
    }
    if (ctx) {
        SSL_CTX_free(ctx);
    }
    ERR_free_strings();
    EVP_cleanup();
}

void get_travel_confirmation_message() {
    SSL_CTX *ctx = NULL;
    SSL *ssl = NULL;
    int server = -1;
    struct sockaddr_in server_addr;
    char request[1000];
    ssize_t numbytes;

    ctx = initialize_ssl_context();
    if (!ctx) goto cleanup;

    server = socket(AF_INET, SOCK_STREAM, 0);
    if (server < 0) {
        perror("Error creating socket");
        goto cleanup;
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(atoi(API2_PORT));
    inet_pton(AF_INET, API2_URL, &server_addr.sin_addr);

    if (connect(server, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Error connecting to server");
        goto cleanup;
    }

    ssl = SSL_new(ctx);
    SSL_set_fd(ssl, server);

    if (SSL_connect(ssl) <= 0) {
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    snprintf(request, sizeof(request), "GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n", API2_ENDPOINT, API2_URL);
    SSL_write(ssl, request, strlen(request));

    while ((numbytes = SSL_read(ssl, request, sizeof(request) - 1)) > 0) {
        request[numbytes] = '\0';
        char *response_data = strstr(request, "{\"message\":");
        if (response_data != NULL) {
            printf("%s\n", response_data);
            break;
        }
    }

    if (numbytes < 0) {
        perror("Error receiving HTTP response");
    }

cleanup:
    if (server >= 0) close(server);
    cleanup_ssl(ssl, ctx);
}

void send_message_confirmation_whatsapp(const char *number, const char *message) {
    SSL_CTX *ctx = NULL;
    SSL *ssl = NULL;
    int server = -1;
    struct sockaddr_in server_addr;
    char request[1500];
    char post_fields[1000];

    snprintf(post_fields, sizeof(post_fields), "{\"numero_telefone\": \"%s\", \"mensagem\": \"%s\"}", number, message);

    ctx = initialize_ssl_context();
    if (!ctx) goto cleanup;

    server = socket(AF_INET, SOCK_STREAM, 0);
    if (server < 0) {
        perror("Error creating socket");
        goto cleanup;
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(atoi(API3_PORT));
    inet_pton(AF_INET, API3_URL, &server_addr.sin_addr);

    if (connect(server, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Error connecting to the server");
        goto cleanup;
    }

    ssl = SSL_new(ctx);
    SSL_set_fd(ssl, server);

    if (SSL_connect(ssl) <= 0) {
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    snprintf(request, sizeof(request), "POST %s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %zu\r\nConnection: close\r\n\r\n%s",
             API3_ENDPOINT, API3_URL, strlen(post_fields), post_fields);
    SSL_write(ssl, request, strlen(request));

    char response[1000];
    ssize_t numbytes;
    while ((numbytes = SSL_read(ssl, response, sizeof(response) - 1)) > 0) {
        response[numbytes] = '\0';
        printf("Response from API3: %s\n", response);
    }

    if (numbytes < 0) {
        perror("Error receiving HTTP response");
    }

cleanup:
    if (server >= 0) close(server);
    cleanup_ssl(ssl, ctx);
}

double extract_total_value(const char *data) {
    const char *total_start = strstr(data, "\"Total\": ");
    if (total_start != NULL) {
        double total;
        sscanf(total_start + strlen("\"Total\": "), "%lf", &total);
        return total;
    }
    return -1.0;
}

char *extract_client_address(const char *data) {
    const char *endereco_start = strstr(data, "\"Endereco\": \"");
    if (endereco_start != NULL) {
        endereco_start += strlen("\"Endereco\": \"");
        const char *endereco_end = strchr(endereco_start, '"');
        if (endereco_end != NULL) {
            size_t address_length = endereco_end - endereco_start;
            char *endereco_cliente = malloc(address_length + 1);
            if (endereco_cliente != NULL) {
                strncpy(endereco_cliente, endereco_start, address_length);
                endereco_cliente[address_length] = '\0';
                return endereco_cliente;
            }
        }
    }
    return NULL;
}

char *extract_client_phone(const char *data) {
    const char *telefone_start = strstr(data, "\"Telefone\": \"");
    if (telefone_start != NULL) {
        telefone_start += strlen("\"Telefone\": \"");
        const char *telefone_end = strchr(telefone_start, '"');
        if (telefone_end != NULL) {
            size_t phone_length = telefone_end - telefone_start;
            char *telefone_cliente = malloc(phone_length + 1);
            if (telefone_cliente != NULL) {
                strncpy(telefone_cliente, telefone_start, phone_length);
                telefone_cliente[phone_length] = '\0';
                return telefone_cliente;
            }
        }
    }
    return NULL;
}

void parse_last_sale() {
    char *start = strrchr(last_sale, '{');
    if (start != NULL) {
        if (last_printed_sale == NULL || strcmp(start, last_printed_sale) != 0) {
            printf("Last sale data:\n");
            printf("%s\n", start);
            if (last_printed_sale != NULL) {
                free(last_printed_sale);
            }
            last_printed_sale = strdup(start);

            double total = extract_total_value(start);
            if (total != -1.0) {
                if (total <= 150) {
                    printf("Total sale value is less than or equal to 150. No trip scheduled.\n");
                } else {
                    char *endereco_cliente = extract_client_address(start);
                    char *telefone_cliente = extract_client_phone(start);
                    if (endereco_cliente != NULL && telefone_cliente != NULL) {
                        schedule_trip(endereco_cliente, telefone_cliente, total);
                        free(endereco_cliente);
                        free(telefone_cliente);
                    } else {
                        printf("Failed to extract address or phone number from last sale data.\n");
                    }
                }
            } else {
                printf("Failed to extract total value from last sale data.\n");
            }
        } else {
            printf("Last sale previously shown.\n");
        }
    }
}

void check_last_sale() {
    SSL_CTX *ctx = NULL;
    SSL *ssl = NULL;
    int server = -1;
    struct sockaddr_in server_addr;
    char request[1000];
    ssize_t numbytes;

    printf("Checking last sale...\n");

    ctx = initialize_ssl_context();
    if (!ctx) goto cleanup;

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(atoi(API1_PORT));
    inet_pton(AF_INET, API1_URL, &server_addr.sin_addr);

    server = socket(AF_INET, SOCK_STREAM, 0);
    if (server < 0) {
        perror("Error creating socket");
        goto cleanup;
    }

    if (connect(server, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Error connecting to server");
        goto cleanup;
    }

    ssl = SSL_new(ctx);
    SSL_set_fd(ssl, server);

    if (SSL_connect(ssl) <= 0) {
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    snprintf(request, sizeof(request), "GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n", API1_ENDPOINT, API1_URL);
    SSL_write(ssl, request, strlen(request));

    while ((numbytes = SSL_read(ssl, request, sizeof(request) - 1)) > 0) {
        request[numbytes] = '\0';
        if (last_sale == NULL) {
            last_sale = malloc(numbytes + 1);
            if (last_sale == NULL) {
                fprintf(stderr, "Failed to allocate memory.\n");
                break;
            }
            memcpy(last_sale, request, numbytes);
            last_sale[numbytes] = '\0';
        } else {
            char *temp = realloc(last_sale, last_sale_size + numbytes + 1);
            if (temp == NULL) {
                fprintf(stderr, "Failed to reallocate memory.\n");
                break;
            }
            last_sale = temp;
            memcpy(last_sale + last_sale_size, request, numbytes);
            last_sale_size += numbytes;
            last_sale[last_sale_size] = '\0';
        }
    }

    if (numbytes < 0) {
        perror("Error receiving HTTP response");
    }

cleanup:
    if (server >= 0) close(server);
    cleanup_ssl(ssl, ctx);

    if (numbytes == 0) {
        parse_last_sale();
    }
}

void schedule_trip(const char *endereco_cliente, const char *telefone_cliente, double valor_total) {
    SSL_CTX *ctx = NULL;
    SSL *ssl = NULL;
    int server = -1;
    struct sockaddr_in server_addr;
    char request[2000];
    char payload[1000];

    ctx = initialize_ssl_context();
    if (!ctx) goto cleanup;

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(atoi(API2_PORT));
    inet_pton(AF_INET, API2_URL, &server_addr.sin_addr);

    server = socket(AF_INET, SOCK_STREAM, 0);
    if (server < 0) {
        perror("Error creating socket");
        goto cleanup;
    }

    if (connect(server, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Error connecting to server");
        goto cleanup;
    }

    ssl = SSL_new(ctx);
    SSL_set_fd(ssl, server);

    if (SSL_connect(ssl) <= 0) {
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    time_t raw_time;
    struct tm *timeinfo;
    time(&raw_time);
    timeinfo = localtime(&raw_time);
    char datetime_str[20];
    strftime(datetime_str, sizeof(datetime_str), "%Y-%m-%d %H:%M", timeinfo);

    snprintf(payload, sizeof(payload), "{\"local_origem\": \"Acme Store\", \"local_destino\": \"%s\", \"telefone_cliente\": \"%s\", \"id_motorista\": 1, \"id_veiculo\": 2, \"id_passageiro\": 3, \"data_hora_inicio\": \"%s\", \"valor\": %.2lf}", endereco_cliente, telefone_cliente, datetime_str, valor_total);

    snprintf(request, sizeof(request), "POST %s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %lu\r\nConnection: close\r\n\r\n%s", API2_ENDPOINT, API2_URL, strlen(payload), payload);
    SSL_write(ssl, request, strlen(request));

    char response[1000];
    ssize_t numbytes;
    while ((numbytes = SSL_read(ssl, response, sizeof(response) - 1)) > 0) {
        response[numbytes] = '\0';
        printf("Response from API2: %s\n", response);
    }

    if (numbytes < 0) {
        perror("Error receiving HTTP response");
    }

cleanup:
    if (server >= 0) close(server);
    cleanup_ssl(ssl, ctx);

    send_message_confirmation_whatsapp(telefone_cliente, "Your trip has been successfully booked. Wait for the car to arrive...!");
}

void *generate_keys(void *arg) {
    char command[256];
    // Atualize o caminho aqui para garantir que está correto
    snprintf(command, sizeof(command), "python3 /home/regis/NB-LOCAL-attestable/launcher/attestable/generate-certificate/generate_certificate.py %d", getpid());
    int ret = system(command);
    if (ret != 0) {
        fprintf(stderr, "Error generating keys\n");
        pthread_exit((void *)1);
    }

    pthread_mutex_lock(&keys_mutex);
    keys_generated = 1;
    pthread_cond_signal(&keys_cond);
    pthread_mutex_unlock(&keys_mutex);

    pthread_exit((void *)0);
}


int main() {
    pthread_t generate_keys_thread;

    // Create and start the thread to generate keys
    if (pthread_create(&generate_keys_thread, NULL, generate_keys, NULL) != 0) {
        fprintf(stderr, "Error creating thread\n");
        return 1;
    }

    // Wait for the keys to be generated
    pthread_mutex_lock(&keys_mutex);
    while (!keys_generated) {
        pthread_cond_wait(&keys_cond, &keys_mutex);
    }
    pthread_mutex_unlock(&keys_mutex);

    while (1) {
        check_last_sale();
        sleep(1); // Checks a new sale every 5 seconds
    }

    // Wait for the keys generation thread to finish
    pthread_join(generate_keys_thread, NULL);

    return 0;
}
