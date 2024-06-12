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

// Definitions for API URLs and ports
#define API1_URL "127.0.0.1"
#define API1_PORT "8000"
#define API1_ENDPOINT "/api/vendas"
#define API2_URL "127.0.0.1"
#define API2_PORT "8001"
#define API2_ENDPOINT "/api/viagens"
#define API3_URL "127.0.0.1"
#define API3_PORT "9000"
#define API3_ENDPOINT "/send-message"

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
int validate_system_info(SSL *ssl);
void display_system_info();

// Variables for tracking the last sale
char *last_sale = NULL;
size_t last_sale_size = 0;
char *last_printed_sale = NULL;

// Variables for synchronization
pthread_mutex_t keys_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t keys_cond = PTHREAD_COND_INITIALIZER;
int keys_generated = 0;

// Function to initialize SSL context
SSL_CTX *initialize_ssl_context() {
    const SSL_METHOD *method;
    SSL_CTX *ctx;

    OpenSSL_add_all_algorithms();
    SSL_load_error_strings();
    method = TLS_client_method();
    ctx = SSL_CTX_new(method);

    if (ctx == NULL) {
        ERR_print_errors_fp(stderr);
        abort();
    }

    const char *cert_file = "provenance/generate-keys/keys/certificate.pem";
    const char *key_file = "provenance/generate-keys/keys/private_key.pem";

    if (access(cert_file, F_OK) == -1) {
        fprintf(stderr, "Certificate file not found: %s\n", cert_file);
        abort();
    }

    if (access(key_file, F_OK) == -1) {
        fprintf(stderr, "Private key file not found: %s\n", key_file);
        abort();
    }

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

// Function to clean up SSL resources
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

// Function to validate system information
int validate_system_info(SSL *ssl) {
    char request[1000];
    snprintf(request, sizeof(request), "POST /api/system-info HTTP/1.1\r\n"
                                       "Host: %s\r\n"
                                       "Content-Type: application/json\r\n"
                                       "Content-Length: %lu\r\n"
                                       "Connection: close\r\n\r\n"
                                       "{"
                                       "\"hostname\": \"GCA\","
                                       "\"program_name\": \"integration_process\","
                                       "\"file_info\": \"/home/regis/TESTE2/https-APIs/integration_process: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=798b0aadbeaac00e9662643cfc5cabe8c6589b76, for GNU/Linux 3.2.0, not stripped\","
                                       "\"cpu_model\": \"Intel(R) Core(TM) i5 CPU       M 450  @ 2.40GHz\","
                                       "\"num_cpus\": 4"
                                       "}", API1_URL, strlen(request));

    SSL_write(ssl, request, strlen(request));

    char response[1000];
    ssize_t numbytes = SSL_read(ssl, response, sizeof(response) - 1);
    if (numbytes > 0) {
        response[numbytes] = '\0';
        printf("Response from API1: %s\n", response);
        return strstr(response, "Valid system information received") != NULL;
    } else {
        perror("Error receiving HTTP response");
        return 0;
    }
}

// Function to display system information
void display_system_info() {
    printf("Attestable:\n");
    printf("{\n");
    printf("    \"hostname\": \"GCA\",\n");
    printf("    \"program_name\": \"integration_process\",\n");
    printf("    \"file_info\": \"/home/regis/TESTE2/https-APIs/integration_process: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=798b0aadbeaac00e9662643cfc5cabe8c6589b76, for GNU/Linux 3.2.0, not stripped\",\n");
    printf("    \"cpu_model\": \"Intel(R) Core(TM) i5 CPU       M 450  @ 2.40GHz\",\n");
    printf("    \"num_cpus\": 4\n");
    printf("}\n");
}

// Function to generate keys
void *generate_keys(void *arg) {
    char command[256];
    snprintf(command, sizeof(command), "python3 provenance/generate-keys/generate_keys.py %d", getpid());
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

// Function to parse the last sale
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

// Function to check the last sale
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

    if (!validate_system_info(ssl)) {
        printf("Invalid system information. Aborting.\n");
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

int main() {
    pthread_t generate_keys_thread;

    // Cria e inicia a thread para gerar chaves
    if (pthread_create(&generate_keys_thread, NULL, generate_keys, NULL) != 0) {
        fprintf(stderr, "Error creating thread\n");
        return 1;
    }

    // Espera até que as chaves sejam geradas
    pthread_mutex_lock(&keys_mutex);
    while (!keys_generated) {
        pthread_cond_wait(&keys_cond, &keys_mutex);
    }
    pthread_mutex_unlock(&keys_mutex);

    // Exibe as informações do sistema uma vez
    display_system_info();

    while (1) {
        check_last_sale();
        sleep(5); // Verifica uma nova venda a cada 5 segundos
    }

    // Espera até que a thread de geração de chaves termine
    pthread_join(generate_keys_thread, NULL);

    return 0;
}

